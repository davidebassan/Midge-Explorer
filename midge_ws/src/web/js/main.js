var app = new Vue({
    el: '#app',
    data: {
        navigation_method: null,
        autonomous: true,
        connected: false,
        ros: null,
        address: '0.0.0.0',
        logs: [],
        topic: null,
        message: null,
        image_topic: null,
        cmd_topic: null,
        navigationViewer: null,
        navigator: null,
        movement_assistant_message: "",
        movement_assistant: null,
        grid: null
    },
    methods : {
        connect: function(){
            console.log('Connessione a rosbridge...')
            this.logs.unshift('Connessione a rosbridge...')
            this.ros = new ROSLIB.Ros({
                url: "ws://" + this.address + ":9090"
            });
            this.ros.on('connection', () => {
                this.connected=true
                console.log('Connesso!')
                this.logs.unshift('Connesso!')
                this.set_camera()
                this.set_navigator()
                this.set_navigation()
                this.set_movement_assistant()
            });
            this.ros.on('error', (error) => {
                console.log('Errore di connessione: ', error)
                this.logs.unshift('Errore di connessione: ', error)
            });
            this.ros.on('close', () => {
                this.connected=false
                console.log('Connessione chiusa')
                this.logs.unshift('Connessione chiusa')
            });
        },

        disconnect: function(){
            this.ros.close()
            this.connected=false
            /* Disconnect also from video and navigator */
        },

        autonomous_function: function(){
            if(this.autonomous){
                this.autonomous = false
                let msg = new ROSLIB.Message({data:'joy'})
                this.navigation_method.publish(msg)
            }
            else{
                this.autonomous = true
                let msg = new ROSLIB.Message({data:'auto'})
                this.navigation_method.publish(msg)
            }
        },

        set_navigation: function(){
            this.navigation_method = new ROSLIB.Topic({
                ros: this.ros,
                name: '/navigation_method',
                messageType: 'std_msgs/String'
            })
        },

        set_movement_assistant: function(){
            this.movement_assistant = new ROSLIB.Topic({
                ros: this.ros,
                name: 'movement_assistant_message',
                messageType: 'std_msgs/String'
            });
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
            this.navigation_viewer = new ROS3D.Viewer({
                divID : 'navigator',
                width : 720,
                height : 540,
                antialias : true,
                intensity : 1.0,
                cameraPose : {x : -1, y : 0, z : 20},
                displayPanAndZoomFrame : true
            });

            this.tf_client = new ROSLIB.TFClient({
                ros : this.ros,
                angularThres : 0.01,
                transThres : 0.01,
                rate : 10.0,
                fixedFrame : '/map'
            });

            this.occupancy_grid = new ROS3D.OccupancyGridClient({
                ros : this.ros,
                rootObject : this.navigation_viewer.scene,
                continuous : true
            });

            this.pose_array = new ROS3D.PoseArray({
                ros: this.ros,
                topic: '/particlecloud',
                tfClient: this.tf_client,
                rootObject: this.navigation_viewer.scene
            });

        },
    },


})



