// Midge Explorer web app (ROS 2 through rosbridge)
const WEBSOCKET_PORT = 9090
const VIDEO_PORT = 8080
const CAMERA_TOPIC = '/camera/rgb/image_raw'

var app = new Vue({
    el: '#app',
    data: {
        address: window.location.hostname || 'localhost',
        connected: false,
        ros: null,
        mode: null,
        modes: [
            {id: 'joy', label: 'Joystick'},
            {id: 'auto', label: 'Autonomo'},
            {id: 'nav', label: 'Nav2'},
            {id: 'stop', label: 'Stop'},
        ],
        obstacle: '-',
        regions: {},
        logs: [],
        topics: {},
        robot_pose: null,
    },
    computed: {
        camera_url: function () {
            return `http://${this.address}:${VIDEO_PORT}/stream?topic=${CAMERA_TOPIC}&type=mjpeg&quality=60`
        },
    },
    methods: {
        log: function (text) {
            const time = new Date().toLocaleTimeString()
            this.logs.unshift(`${time}  ${text}`)
            this.logs.splice(100)
        },

        connect: function () {
            this.log('Connessione a rosbridge...')
            this.ros = new ROSLIB.Ros({url: `ws://${this.address}:${WEBSOCKET_PORT}`})
            this.ros.on('connection', () => {
                this.connected = true
                this.log('Connesso!')
                this.set_topics()
                this.$nextTick(() => this.set_map())
                this.joystick_timer = setInterval(this.publish_joystick, 100)
            })
            this.ros.on('error', () => this.log('Errore di connessione a ' + this.address))
            this.ros.on('close', () => {
                if (this.connected) this.log('Connessione chiusa')
                this.connected = false
                clearInterval(this.joystick_timer)
            })
        },

        topic: function (name, messageType) {
            return new ROSLIB.Topic({ros: this.ros, name: name, messageType: messageType})
        },

        set_topics: function () {
            this.topics.mode = this.topic('/navigation_method', 'std_msgs/msg/String')
            this.topics.joy = this.topic('/joy', 'sensor_msgs/msg/Joy')
            this.topics.goal = this.topic('/goal_pose', 'geometry_msgs/msg/PoseStamped')
            // Advertise now: a publisher created on the first click can lose that message
            Object.values(this.topics).forEach((t) => t.advertise())

            this.topic('/midge/status', 'std_msgs/msg/String').subscribe((msg) => {
                const status = JSON.parse(msg.data)
                this.mode = status.mode
                this.obstacle = status.obstacle
                this.regions = status.regions
            })
            this.topic('/movement_assistant', 'std_msgs/msg/String').subscribe((msg) => {
                this.log('Movement assistant: ' + msg.data)
            })
            this.topic('/midge/pose', 'geometry_msgs/msg/PoseStamped').subscribe((msg) => {
                this.robot_pose = msg.pose
                this.update_robot_marker()
            })
        },

        set_mode: function (mode) {
            this.topics.mode.publish(new ROSLIB.Message({data: mode}))
            this.log('Modalità: ' + mode)
        },

        // Map of slam_toolbox with the robot and click-to-goal for Nav2
        set_map: function () {
            // Fixed canvas resolution, CSS scales it to the column width
            const W = 640, H = 480
            document.getElementById('map').innerHTML = ''
            this.viewer = new ROS2D.Viewer({divID: 'map', width: W, height: H})

            const grid = new ROS2D.OccupancyGridClient({
                ros: this.ros, rootObject: this.viewer.scene, continuous: true, topic: '/map'})
            grid.on('change', () => {
                // Same scale on both axes (no stretching), map centred in the canvas
                const g = grid.currentGrid
                const metersPerPixel = Math.max(g.width / W, g.height / H)
                this.viewer.scaleToDimensions(W * metersPerPixel, H * metersPerPixel)
                this.viewer.shift(g.pose.position.x - (W * metersPerPixel - g.width) / 2,
                                  g.pose.position.y - (H * metersPerPixel - g.height) / 2)
                // keep markers above the map
                this.viewer.scene.addChild(this.robot_marker)
                this.viewer.scene.addChild(this.goal_marker)
            })

            // Robot: a disc as wide as Midge with a line showing where it faces
            this.robot_marker = new createjs.Shape()
            this.robot_marker.graphics
                .beginFill('rgba(255, 128, 0, 0.9)').drawCircle(0, 0, 0.25).endFill()
                .setStrokeStyle(0.06).beginStroke('#000').moveTo(0, 0).lineTo(0.35, 0).endStroke()
            this.robot_marker.visible = false
            this.goal_marker = new createjs.Shape()
            this.goal_marker.graphics.beginFill('#22cc55').drawCircle(0, 0, 0.15)
            this.goal_marker.visible = false
            this.viewer.scene.addChild(this.robot_marker)
            this.viewer.scene.addChild(this.goal_marker)

            this.viewer.scene.on('stagemousedown', (event) => {
                if (this.mode !== 'nav') return
                const point = this.viewer.scene.globalToRos(event.stageX, event.stageY)
                this.send_goal(point.x, point.y)
            })
        },

        update_robot_marker: function () {
            if (!this.robot_marker || !this.robot_pose) return
            this.robot_marker.x = this.robot_pose.position.x
            this.robot_marker.y = -this.robot_pose.position.y
            this.robot_marker.rotation = this.viewer.scene.rosQuaternionToGlobalTheta(this.robot_pose.orientation)
            this.robot_marker.visible = true
        },

        send_goal: function (x, y) {
            // Face the direction of travel so the robot does not spin on arrival
            let yaw = 0
            if (this.robot_pose) {
                yaw = Math.atan2(y - this.robot_pose.position.y, x - this.robot_pose.position.x)
            }
            this.topics.goal.publish(new ROSLIB.Message({
                header: {frame_id: 'map', stamp: {sec: 0, nanosec: 0}},
                pose: {
                    position: {x: x, y: y, z: 0},
                    orientation: {x: 0, y: 0, z: Math.sin(yaw / 2), w: Math.cos(yaw / 2)},
                },
            }))
            this.goal_marker.x = x
            this.goal_marker.y = -y
            this.goal_marker.visible = true
            this.log(`Obiettivo Nav2: x=${x.toFixed(2)} y=${y.toFixed(2)}`)
        },

        // Web joystick -> /joy (axes[0] = turn, left positive; axes[1] = forward)
        publish_joystick: function () {
            if (this.mode !== 'joy' || !this.topics.joy) return
            const pos = joystick.getPosition()
            const axes = [-pos.x / joystick.maxDiff, -pos.y / joystick.maxDiff]
            if (axes[0] === 0 && axes[1] === 0 && this.joystick_idle) return
            this.joystick_idle = axes[0] === 0 && axes[1] === 0
            this.topics.joy.publish(new ROSLIB.Message({
                header: {frame_id: 'web', stamp: {sec: 0, nanosec: 0}},
                axes: axes,
                buttons: [],
            }))
        },
    },
})

// Created after Vue has rendered the page, so the stick keeps its listeners
var joystick = createJoystick(document.getElementById('joystick'))

// Connect straight away when the page is served by the robot itself
if (window.location.hostname) {
    app.connect()
}
