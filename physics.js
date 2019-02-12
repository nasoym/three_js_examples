// Set up the scene, camera, and renderer as global variables.
var scene, camera, renderer;
var cube ;

document.onreadystatechange = function () {
  if (document.readyState === "complete") {
    init();
    animate();
    // var ws = new WebSocket('ws://localhost:8765');
    // ws.addEventListener('message', function (event) {
    //     console.log('Message from server ', event.data);
    // });


    // Stomp.js boilerplate
    // var client = Stomp.client('ws://' + window.location.hostname + ':15674/ws');
    // var client = Stomp.client('ws://localhost:32784/ws');
    var client = Stomp.client('ws://localhost:8080/ws');
    // client.debug = pipe('#second');

    var on_connect = function(x) {
        // id = client.subscribe("/topic/test", function(d) {
        id = client.subscribe("/queue/updates", function(d) {
            // console.log("::: " + d);
            // console.log("::: " , d.body);
            // console.log("::: " , typeof JSON.parse(d.body));
            console.log("::: " , JSON.parse(d.body));
            //  print_first(d.body);
            // console.log("::: " , cube);
            // console.log("::: " , cube.position);

            // var body = JSON.parse(d.body);
            // cube.position = new THREE.Vector3(body.pos[0],body.pos[1],body.pos[2]);
            // console.log("::: " , cube.position);
            // console.log("::: " , cube);

        });
    };
    var on_error =  function() {
      console.log('error');
    };
    client.connect('guest', 'guest', on_connect, on_error, '/');

  }
};

// Sets up the scene.
function init() {

  // Create the scene and set the scene size.
  scene = new THREE.Scene();
  var WIDTH = window.innerWidth,
      HEIGHT = window.innerHeight;

  // Create a renderer and add it to the DOM.
  renderer = new THREE.WebGLRenderer({antialias:true});
  renderer.setSize(WIDTH, HEIGHT);
  document.body.appendChild(renderer.domElement);

  // Create a camera, zoom it out from the model a bit, and add it to the scene.
  camera = new THREE.PerspectiveCamera(45, WIDTH / HEIGHT, 0.1, 20000);
  // camera.position.set(0,15,0);

  // camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );
  // camera.position.z = 1;
  // camera.position.y = -5;
  // camera.rotateOnAxis(new THREE.Vector3(1, 0, 0), degInRad(90));
  // camera.rotation.order = 'YXZ';
  // camera.up = new THREE.Vector3(0, 0, 1);  
  camera.position.set(30,30,30);
  camera.up = new THREE.Vector3(0,0,1);
  camera.lookAt(new THREE.Vector3(0,0,0));

  scene.add(camera);

  // Create an event listener that resizes the renderer with the browser window.
  window.addEventListener('resize', function() {
    var WIDTH = window.innerWidth,
        HEIGHT = window.innerHeight;
    renderer.setSize(WIDTH, HEIGHT);
    camera.aspect = WIDTH / HEIGHT;
    camera.updateProjectionMatrix();
  });

  // Set the background color of the scene.
  renderer.setClearColor(new THREE.Color(0x333F47, 1));

  // Create a light, set its position, and add it to the scene.
  var light = new THREE.PointLight(0xffffff);
  light.position.set(100,100,100);
  scene.add(light);

  // // Load in the mesh and add it to the scene.
  // var loader = new THREE.JSONLoader();
  // loader.load( "models/treehouse_logo.js", function(geometry){
  //   var material = new THREE.MeshLambertMaterial({color: 0x55B663});
  //   mesh = new THREE.Mesh(geometry, material);
  //   scene.add(mesh);
  // });

  // var geometry = new THREE.BoxGeometry( 1, 1, 1 );
  // var geometry = new THREE.BoxGeometry(700, 700, 700, 10, 10, 10);

  // var material = new THREE.MeshBasicMaterial( {color: 0x00ff00} );
  // var cube = new THREE.Mesh( geometry, material );
  // scene.add( cube );

    // // var material = new THREE.MeshLambertMaterial({color: 0x55B663});
    // // var material = new THREE.MeshPhongMaterial({color: 0x55B663});
    // var material = new THREE.MeshBasicMaterial({color: 0x55B663, wireframe: false});
    // var material2 = new THREE.MeshBasicMaterial({color: 0x050603, wireframe: true,wireframeLinewidth:3});
    //
    // // cube = new THREE.Mesh( new THREE.CubeGeometry( 1, 1, 1 ), material);
    // cube = THREE.SceneUtils.createMultiMaterialObject( new THREE.CubeGeometry( 1, 1, 1 ), [material,material2]);
    // cube.position.set(0, 0, 20);
    // cube.scale.set(1,1,1);
    // cube.quaternion.set(0,0,0,1);
    // scene.add( cube );
    //
    // // cube = new THREE.Mesh( new THREE.CubeGeometry( 1, 1, 1 ), material);
    // cube = THREE.SceneUtils.createMultiMaterialObject( new THREE.CubeGeometry( 1, 1, 1 ), [material,material2]);
    // cube.position.set(0, 0, 10);
    // cube.scale.set(1,1,1);
    // cube.quaternion.set(0,0,0,1);
    // scene.add( cube );
    //
    // // cube = new THREE.Mesh( new THREE.CubeGeometry( 1, 1, 1 ), material);
    // cube = THREE.SceneUtils.createMultiMaterialObject( new THREE.CubeGeometry( 1, 1, 1 ), [material,material2]);
    // cube.position.set(0, 0, 5);
    // cube.scale.set(1,5,1);
    // cube.quaternion.set(0,0,0,1);
    // cube.userData = { "foo" : "bla" };
    // cube.name="foo";
    // scene.add( cube );
    //
    //
    // // cube = new THREE.Mesh( new THREE.CubeGeometry( 1, 1, 1 ), material);
    // cube = THREE.SceneUtils.createMultiMaterialObject( new THREE.CubeGeometry( 1, 1, 1 ), [material,material2]);
    // cube.position.set(0, 10, 0);
    // cube.scale.set(1,1,1);
    // cube.quaternion.set(0,0,0,1);
    // scene.add( cube );
    //
    // // var plane = new THREE.Mesh(new THREE.PlaneGeometry( 2000, 2000 ),material);
    // // var plane = new THREE.Mesh(new THREE.PlaneGeometry(60,40,1,1),material);
    // var plane = new THREE.Mesh(new THREE.PlaneGeometry(10,10,1,1),material);
    // plane.quaternion.set(0,0,0,1);
    // scene.add(plane);
    //
    // console.log("object foo ", scene.getObjectByName("foo"));


    scene.traverse (function (object) {
      if (object instanceof THREE.Mesh) {
        console.log("---: ",object);
      }
    });


  // Add OrbitControls so that we can pan around with the mouse.
  controls = new THREE.OrbitControls(camera, renderer.domElement);

}


// Renders the scene and updates the render as needed.
function animate() {

  // Read more about requestAnimationFrame at http://www.paulirish.com/2011/requestanimationframe-for-smart-animating/
  requestAnimationFrame(animate);
  
  // Render the scene.
  renderer.render(scene, camera);
  controls.update();

}


