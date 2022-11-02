const colors = [
  "rgb(72,123,166)", "rgb(247,142,50)", "rgb(87,157,82)", "rgb(229,93,90)",
  "rgb(241,197,79)", "rgb(114,181,178)", "rgb(177,126,160)", "rgb(255,160,167)",
  "rgb(158,117,96)", "rgb(186,176,172)"
];
const inner_circle_color = "rgb(255,255,255)";
const translation = [0.0, 0.0, 0.0];
const scale = 1.0;

// from https://stackoverflow.com/questions/5560248/programmatically-lighten-or-darken-a-hex-color-or-rgb-and-blend-colors
const shadeRGBColor = (color, percent) => {
  const f = color.split(",");
  const t = percent < 0 ? 0 : 255;
  const p = percent < 0 ? percent * -1 : percent;
  const R = parseInt(f[0].slice(4));
  const G = parseInt(f[1]);
  const B = parseInt(f[2]);

  return "rgb(" + (Math.round((t - R) * p) + R) + "," + (Math.round((t - G) * p) + G) + "," + (Math.round((t - B) * p) + B) + ")";
}

const sigmoidInterp = (x, a) => {
  const e1 = Math.exp(-a * (2.0 * x - 1));
  const e2 = Math.exp(-a);

  return 0.5 * (1.0 + (1.0 - e1) * (1.0 + e2) / (1.0 + e1) / (1.0 - e2));
}

const renderCanvases = ({
  texture = null
} = {}) => {
  const width = document.getElementById("canvas").clientWidth - 1;
  const height = document.getElementById("canvas").clientHeight - 1;
  const sizePerVertex = 9;
  const vertices = data.meshes;
  const categories = data.meshCategories;
  const centralNodeCate = data.centralNodeCategory;
  const numMeshesForEachBranch = data.numMeshesForEachBranch;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, width / height, 1, 1000);
  camera.position.x = 0;
  camera.position.z = 1.5;
  scene.add(camera);

  // lighting
  const light = new THREE.DirectionalLight(0xffffff, 1.5);
  light.position.set(0.5, 0.5, 1).normalize();
  scene.add(light);
  const light2 = new THREE.DirectionalLight(0xffffff, 0.5);
  light2.position.set(-0.4, -0.2, 1).normalize();
  scene.add(light2);

  // renderer
  renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true
  });
  renderer.setSize(width, height);
  renderer.setPixelRatio(window.devicePixelRatio || 1);

  // prepare canvas for rendering
  document.getElementById("canvas").appendChild(renderer.domElement);

  for (let i = 0; i < vertices.length / sizePerVertex; i++) {
    const category = categories[i];
    const ratio = category != -1 && category != centralNodeCate ?
      1.0 - (i % numMeshesForEachBranch) / numMeshesForEachBranch :
      1.0;

    const colStr = category == -1 ?
      new THREE.Color(inner_circle_color) :
      (category == centralNodeCate ?
        new THREE.Color(colors[category]) :
        new THREE.Color(shadeRGBColor(colors[category], sigmoidInterp(ratio - 0.4, 4.0))));

    const material = new THREE.MeshBasicMaterial({
      color: colStr,
      transparent: true,
      opacity: ratio + 0.2
    });

    const radius = Math.sqrt(vertices[i * sizePerVertex + 6] * vertices[i * sizePerVertex + 6] + vertices[i * sizePerVertex + 7] * vertices[i * sizePerVertex + 7])
    const v1 = new THREE.Vector3(parseFloat(vertices[i * sizePerVertex + 0]), parseFloat(vertices[i * sizePerVertex + 1]), parseFloat(vertices[i * sizePerVertex + 2]));
    const v2 = new THREE.Vector3(parseFloat(vertices[i * sizePerVertex + 3]), parseFloat(vertices[i * sizePerVertex + 4]), parseFloat(vertices[i * sizePerVertex + 5]));
    const v3 = new THREE.Vector3(parseFloat(vertices[i * sizePerVertex + 6]), parseFloat(vertices[i * sizePerVertex + 7]), parseFloat(vertices[i * sizePerVertex + 8]));
    const points = [v1, v2, v3];

    const geometry = category == -1 ? new THREE.CircleGeometry(radius, 32) : new THREE.BufferGeometry().setFromPoints(points);
    if (category == -1) {
      // paste texture for inner circle
      material.map = texture;
      material.transparent = true;
      material.opacity = 1.0;
    }

    const mesh = new THREE.Mesh(geometry, material);
    mesh.scale.copy(new THREE.Vector3(scale, scale, scale));
    scene.add(mesh);
  }
  renderer.render(scene, camera);
}

const draw = () => {
  const textureLoader = new THREE.TextureLoader();
  textureLoader.crossOrigin = "";
  textureLoader.load("textures/texture1.png", texture => {
    const texture1 = texture;
    renderCanvases({
      texture: texture
    });
  });
}