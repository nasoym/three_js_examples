var scene, camera, renderer;

function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
  controls.update();
  stats.update();
}

function render() {
  renderer.render( scene, camera );
}

function init() {
  scene = new THREE.Scene();
  var WIDTH = window.innerWidth,
      HEIGHT = window.innerHeight;

  renderer = new THREE.WebGLRenderer({antialias:true});
  renderer.setSize(WIDTH, HEIGHT);
  document.body.appendChild(renderer.domElement);

  camera = new THREE.PerspectiveCamera(45, WIDTH / HEIGHT, 0.1, 20000);
  // camera.rotateOnAxis(new THREE.Vector3(1, 0, 0), degInRad(90));
  // camera.rotation.order = 'YXZ';
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

  renderer.setClearColor(new THREE.Color(0x333F47, 1));

  var light = new THREE.PointLight(0xffffff);
  light.position.set(100,100,100);
  scene.add(light);

  // controls = new THREE.OrbitControls(camera, renderer.domElement);

  controls = new THREE.TrackballControls( camera );
  controls.rotateSpeed = 1.0;
  controls.zoomSpeed = 1.2;
  controls.panSpeed = 0.8;
  controls.noZoom = false;
  controls.noPan = false;
  controls.staticMoving = true;
  controls.dynamicDampingFactor = 0.3;
  controls.keys = [ 65, 83, 68 ];
  controls.addEventListener( 'change', render );

  stats = new Stats();
  document.body.appendChild( stats.dom );

}

function create_body(data) {

  var id = data["id"];
  // var material = new THREE.MeshLambertMaterial({color: 0x55B663});
  var material = new THREE.MeshPhongMaterial({color: 0x55B663});
  var material_color = new THREE.MeshBasicMaterial({color: 0x55B663, wireframe: false});
  var material_wireframe = new THREE.MeshBasicMaterial({color: 0x050603, wireframe: true, wireframeLinewidth:3});

  console.log("create body with id: ", id);

  if (data.hasOwnProperty("type")) {
    var type = data["type"];
    if (type === "box" ) {
      console.log("create box");
      body = THREE.SceneUtils.createMultiMaterialObject( 
          new THREE.CubeGeometry( 1, 1, 1 ), 
          [material,material_wireframe]
        );
          // [material_color,material_wireframe]
    } else if (type === "plane" ) {
      console.log("create plane");
      // 2nd and 3rd argument are the vertical / horizontal segments
      body = THREE.SceneUtils.createMultiMaterialObject( 
          new THREE.PlaneGeometry( 1, 1 ), 
          [material,material_wireframe]
        );
          // [material_color,material_wireframe]
    // } else if (type === "sphere" ) {
    }
  }
  // body.userData = { "foo" : "bla" };
  // body.name="foo";
  body.id = id;
  scene.add( body );
  return body;
}

function update_body(data) {
  var body = scene.getObjectById(data["id"]);
  if (typeof body === "undefined") {
    body = create_body(data);
  }
  if (data.hasOwnProperty("pos")) {
    body.position.set(data["pos"][0],data["pos"][1],data["pos"][2]);
  }
  if (data.hasOwnProperty("rot")) {
    // console.log(data["rot"][0],data["rot"][1],data["rot"][2],data["rot"][3]);
    body.quaternion.set(data["rot"][0],data["rot"][1],data["rot"][2],data["rot"][3]);
  }
  if (data.hasOwnProperty("size")) {
    body.scale.set(data["size"][0],data["size"][1],data["size"][2]);
  }
}

function update_bodies(data) {
  var all_ids = [];
  scene.traverse (function (object) {
    if (object instanceof THREE.Mesh) {
      all_ids.push(object.parent.id);
    }
  });
  var id;
  for (i in data) {
    update_body(data[i]);
    id = data[i]["id"];
    all_ids = all_ids.filter(function(val,i,a) {return val !== id;})
  }

  // console.log("unused ids: ",all_ids);
  for (i in all_ids) {
    console.log("remove : ",all_ids[i]);
    scene.remove(scene.getObjectById(all_ids[i]));
  }
}

function setup_update_listener(address,exchange_name) {
  // Stomp.js boilerplate
  var client = Stomp.client('ws://' + address + '/ws');
  client.debug = function(a,b) { };

  var on_connect = function(x) {
    id = client.subscribe("/exchange/"+exchange_name, function(d) {
      update_bodies(JSON.parse(d.body));
    });
  };
  var on_error =  function() {
    console.log('error');
  };
  client.connect('guest', 'guest', on_connect, on_error, '/');
}

document.onreadystatechange = function () {
  if (document.readyState === "complete") {

    var urlParams = new URLSearchParams(window.location.search);
    var host = window.location.hostname;
    // var port = 15674;
    var port = 8080;
    var exchange_name = "updates";
    if (urlParams.has('host')) {
      host = urlParams.get('host');
    }
    if (host === "" ) {
      host = "localhost";
    }
    if (urlParams.has('port')) {
      port = urlParams.get('port');
    }
    if (urlParams.has('exchange')) {
      exchange_name = urlParams.get('exchange');
    }

    init();
    animate();
    setup_update_listener(host + ":" + port, exchange_name);
  }
};

