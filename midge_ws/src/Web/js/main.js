var app = new Vue({
    el: '#app',
    data: {
        connected: false,
        ros: null,
        address: '0.0.0.0',
        logs: [],
        topic: null,
        message: null,
        image_topic: null,
        cmd_topic: null,
        navigationViewer: null,
        navigator: null
    },

    methods : {
        connect: function(){
            console.log('Connessione a rosbridge...')
            this.logs.unshift('Connessione a rosbridge...')
            this.ros = new ROSLIB.Ros({
                url: "ws://" + this.address + ":9090"
            })
            this.ros.on('connection', () => {
                this.connected=true
                console.log('Connesso!')
                this.logs.unshift('Connesso!')
                this.set_camera()
                this.set_navigator()
            })
            this.ros.on('error', (error) => {
                console.log('Errore di connessione: ', error)
                this.logs.unshift('Errore di connessione: ', error)
            })
            this.ros.on('close', () => {
                this.connected=false
                console.log('Connessione chiusa')
                this.logs.unshift('Connessione chiusa')
            })
        },
        disconnect: function(){
            this.ros.close()
            this.connected=false
        },
        set_camera: function(){
            this.cameraViewer = new MJPEGCANVAS.Viewer({
                divID: 'live_camera',
                host: this.address,
                width: 720,
                height: 540,
                topic: '/camera/rgb/image_raw',
                port: 8080,
            })
        },

        set_navigator: function(){
            this.navigationViewer = new ROS2D.Viewer({
                divID: 'navigator',
                height: 540,
                width: 540
            });



        }
        /*
        set_cmd: function(){
            this.cmd_topic = new ROSLIB.Topic({
                ros: this.ros,
                name: '/cmd_vel',
                messageType: 'geometry_msgs/Twist',
            })
        }

        move: function(){
            this.message = new ROSLIB.Message({
                linear: linear,
                angular: angular
            })
            this.set_cmd()
            this.cmd_topic.publish(this.message)
        }

        stop: function(linear, angular){
            this.message = new ROSLIB.Message({
                linear: {x: 0, y:0, z: 0},
                angular: {x: 0, y:0, z:0}
            })
            this.set_cmd()
            this.cmd_topic.publish(this.message)
        }*/
    },
})
