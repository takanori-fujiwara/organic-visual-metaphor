var colors = ["rgb(72,123,166)", "rgb(247,142,50)", "rgb(87,157,82)", "rgb(229,93,90)", "rgb(241,197,79)",
    "rgb(114,181,178)", "rgb(177,126,160)", "rgb(255,160,167)", "rgb(158,117,96)", "rgb(186,176,172)"
];
var inner_circle_color = "rgb(255,255,255)";
var translation = [0.0, 0.0, 0.0];
var scale = 1.0;
var texture1;
var texture2;

function loadTextures() {
    var textureLoader = new THREE.TextureLoader();
    textureLoader.crossOrigin = '';
    textureLoader.load('textures/texture1.png', function(texture) {
        texture1 = texture;
    });
    textureLoader.load('textures/texture2.png', function(texture) {
        texture2 = texture;
    });
}

// from https://stackoverflow.com/questions/5560248/programmatically-lighten-or-darken-a-hex-color-or-rgb-and-blend-colors
function shadeRGBColor(color, percent) {
    var f = color.split(","),
        t = percent < 0 ? 0 : 255,
        p = percent < 0 ? percent * -1 : percent,
        R = parseInt(f[0].slice(4)),
        G = parseInt(f[1]),
        B = parseInt(f[2]);
    return "rgb(" + (Math.round((t - R) * p) + R) + "," + (Math.round((t - G) * p) + G) + "," + (Math.round((t - B) * p) + B) + ")";
}

function sigmoidInterp(x, a) {
    e1 = Math.exp(-a * (2.0 * x - 1));
    e2 = Math.exp(-a);
    return 0.5 * (1.0 + (1.0 - e1) * (1.0 + e2) / (1.0 + e1) / (1.0 - e2));
}

function renderCanvases() {
    var width = document.getElementById('canvas').clientWidth - 1;
    var height = document.getElementById('canvas').clientHeight - 1;
    console.log(width, height)
    var sizePerVertex = 9;
    var vertices = data.meshes;
    var categories = data.meshCategories;
    var centralNodeCate = data.centralNodeCategory;
    var numMeshesForEachBranch = data.numMeshesForEachBranch;

    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera( 40, width / height, 1, 1000 );
    camera.position.x = 0;
    camera.position.z = 1.5;
    scene.add( camera );

    // lighting
    var light = new THREE.DirectionalLight( 0xffffff, 1.5 );
    light.position.set( 0.5, 0.5, 1 ).normalize();
    scene.add( light );
    var light2 = new THREE.DirectionalLight( 0xffffff, 0.5 );
    light2.position.set( -0.4, -0.2, 1 ).normalize();
    scene.add( light2 );

    // renderer
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize( width, height );
    renderer.setPixelRatio(window.devicePixelRatio || 1);

    // prepare canvas for rendering
    document.getElementById('canvas').appendChild(renderer.domElement);

    for (var i = 0; i < vertices.length / sizePerVertex; i++) {
        var category = categories[i];
        var geometry = new THREE.Geometry();
        var ratio = 1.0;
        if (category != -1 && category != centralNodeCate) {
            ratio = 1.0 - (i % numMeshesForEachBranch) / numMeshesForEachBranch;
        }

        var colStr;
        if (category == -1) {
            colStr = new THREE.Color(inner_circle_color);
        } else {
            if (category == centralNodeCate) {
                colStr = new THREE.Color(colors[category]);
            } else {
                colStr = new THREE.Color(shadeRGBColor(colors[category], sigmoidInterp(ratio - 0.4, 4.0)));
            }
        }

        var material = new THREE.MeshBasicMaterial({
            color: colStr,
            transparent: true,
            opacity: ratio + 0.2
        });

        if (category == -1) {
            // paste texture for inner circle
            var radius = Math.sqrt(vertices[i * sizePerVertex + 6] * vertices[i * sizePerVertex + 6] + vertices[i * sizePerVertex + 7] * vertices[i * sizePerVertex + 7])
            geometry = new THREE.CircleGeometry(radius, 32);
            material.map = texture1;
            material.transparent = true;
            material.opacity = 1.0;
            // material.opacity = 0.07;
        } else {
            var v1 = new THREE.Vector3(parseFloat(vertices[i * sizePerVertex + 0]), parseFloat(vertices[i * sizePerVertex + 1]), parseFloat(vertices[i * sizePerVertex + 2]));
            var v2 = new THREE.Vector3(parseFloat(vertices[i * sizePerVertex + 3]), parseFloat(vertices[i * sizePerVertex + 4]), parseFloat(vertices[i * sizePerVertex + 5]));
            var v3 = new THREE.Vector3(parseFloat(vertices[i * sizePerVertex + 6]), parseFloat(vertices[i * sizePerVertex + 7]), parseFloat(vertices[i * sizePerVertex + 8]));
            geometry.vertices.push(v1);
            geometry.vertices.push(v2);
            geometry.vertices.push(v3);
            // compute normals
            geometry.faces.push(new THREE.Face3(0, 1, 2));
        }

        var mesh = new THREE.Mesh(geometry, material);

        mesh.geometry.mergeVertices();
        mesh.geometry.applyMatrix(
            new THREE.Matrix4().makeTranslation(translation[0], translation[1], translation[2])
        );
        mesh.scale.copy(new THREE.Vector3(scale, scale, scale));

        scene.add(mesh);

    }
    renderer.render(scene, camera);
}

function draw() {
    if (!texture1 || !texture2) { // in case of texture is still finished to load
        var textureLoader = new THREE.TextureLoader();
        textureLoader.crossOrigin = '';

        textureLoader.load('textures/texture1.png', function(texture) {
            texture1 = texture;
            textureLoader.load('textures/texture2.png', function(texture) {
                texture2 = texture;
                renderCanvases();
            });
        });
    } else {
        renderCanvases();
    }
}
