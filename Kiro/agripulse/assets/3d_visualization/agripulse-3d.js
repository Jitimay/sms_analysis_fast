class AgriPulse3D {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;

        // Central Burundi map
        this.centralNode = null;
        this.regions = [];

        // Orbiting satellites (data streams)
        this.satellites = [];
        this.satelliteData = [
            { name: 'Coffee Prices', type: 'prices', status: 'threat', angle: 0 },
            { name: 'Weather Data', type: 'weather', status: 'watch', angle: Math.PI / 3 },
            { name: 'Disease Reports', type: 'disease', status: 'opportunity', angle: 2 * Math.PI / 3 },
            { name: 'Market Data', type: 'market', status: 'watch', angle: Math.PI },
            { name: 'News Feed', type: 'news', status: 'threat', angle: 4 * Math.PI / 3 },
            { name: 'Exchange Rates', type: 'currency', status: 'opportunity', angle: 5 * Math.PI / 3 }
        ];

        // Connection lines and pulses
        this.connections = [];
        this.pulses = [];

        // Animation properties
        this.time = 0;
        this.orbitRadius = 8;
        this.orbitSpeed = 0.01;

        this.init();
    }

    init() {
        this.createScene();
        this.createCentralNode();
        this.createSatellites();
        this.createConnections();
        this.setupLighting();
        this.setupControls();
        this.animate();

        // Hide loading screen
        document.getElementById('loading').style.display = 'none';

        // Start data simulation
        this.simulateDataStreams();
    }

    createScene() {
        // Scene setup
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0a0a);

        // Camera setup
        this.camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        this.camera.position.set(0, 5, 15);

        // Renderer setup
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        document.getElementById('container').appendChild(this.renderer.domElement);

        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());
    }

    createCentralNode() {
        // Create Burundi map representation (simplified as a textured plane)
        const geometry = new THREE.PlaneGeometry(4, 3);
        const material = new THREE.MeshPhongMaterial({
            color: 0x6F4E37,
            transparent: true,
            opacity: 0.8
        });

        this.centralNode = new THREE.Mesh(geometry, material);
        this.centralNode.rotation.x = -Math.PI / 2;
        this.scene.add(this.centralNode);

        // Add coffee regions as glowing points
        this.createCoffeeRegions();

        // Add pulsing ring around central node
        this.createPulsingRing();
    }

    createCoffeeRegions() {
        const regionData = [
            { name: 'Kayanza', x: -1, z: 0.5, status: 'watch' },
            { name: 'Ngozi', x: 0.5, z: 1, status: 'threat' },
            { name: 'Muyinga', x: 1.2, z: -0.5, status: 'opportunity' }
        ];

        regionData.forEach(region => {
            const geometry = new THREE.SphereGeometry(0.1, 16, 16);
            const color = this.getStatusColor(region.status);
            const material = new THREE.MeshPhongMaterial({
                color: color,
                emissive: color,
                emissiveIntensity: 0.3
            });

            const regionMesh = new THREE.Mesh(geometry, material);
            regionMesh.position.set(region.x, 0.1, region.z);
            regionMesh.userData = region;

            this.regions.push(regionMesh);
            this.scene.add(regionMesh);

            // Add glowing effect
            this.addGlowEffect(regionMesh, color);

            // Make regions clickable
            regionMesh.userData.clickable = true;
        });
    }

    createPulsingRing() {
        const geometry = new THREE.RingGeometry(3, 3.2, 32);
        const material = new THREE.MeshBasicMaterial({
            color: 0x6F4E37,
            transparent: true,
            opacity: 0.3,
            side: THREE.DoubleSide
        });

        const ring = new THREE.Mesh(geometry, material);
        ring.rotation.x = -Math.PI / 2;
        ring.position.y = 0.01;
        this.scene.add(ring);

        // Animate ring pulsing
        this.pulsingRing = ring;
    }

    createSatellites() {
        this.satelliteData.forEach((data, index) => {
            const satellite = this.createSatellite(data);
            this.satellites.push(satellite);
            this.scene.add(satellite.group);
        });
    }

    createSatellite(data) {
        const group = new THREE.Group();

        // Main satellite body
        const geometry = new THREE.BoxGeometry(0.3, 0.3, 0.3);
        const color = this.getStatusColor(data.status);
        const material = new THREE.MeshPhongMaterial({
            color: color,
            emissive: color,
            emissiveIntensity: 0.2
        });

        const mesh = new THREE.Mesh(geometry, material);
        group.add(mesh);

        // Add data stream visualization
        this.addDataStreamEffect(group, data);

        // Add label
        this.addSatelliteLabel(group, data.name);

        return {
            group: group,
            data: data,
            mesh: mesh
        };
    }

    addDataStreamEffect(group, data) {
        // Create particle system for data streams
        const particleCount = 20;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);

        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 2;
            positions[i * 3 + 1] = (Math.random() - 0.5) * 2;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 2;
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

        const material = new THREE.PointsMaterial({
            color: this.getStatusColor(data.status),
            size: 0.05,
            transparent: true,
            opacity: 0.6
        });

        const particles = new THREE.Points(geometry, material);
        group.add(particles);

        group.userData.particles = particles;
    }

    addSatelliteLabel(group, text) {
        // Create text label (simplified - in production, use TextGeometry or HTML overlay)
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 256;
        canvas.height = 64;

        context.fillStyle = 'rgba(0, 0, 0, 0.8)';
        context.fillRect(0, 0, canvas.width, canvas.height);

        context.fillStyle = 'white';
        context.font = '16px Arial';
        context.textAlign = 'center';
        context.fillText(text, canvas.width / 2, canvas.height / 2 + 6);

        const texture = new THREE.CanvasTexture(canvas);
        const material = new THREE.SpriteMaterial({ map: texture });
        const sprite = new THREE.Sprite(material);
        sprite.scale.set(2, 0.5, 1);
        sprite.position.y = 0.8;

        group.add(sprite);
    }

    createConnections() {
        // Create connection lines between satellites and central node
        this.satellites.forEach(satellite => {
            const geometry = new THREE.BufferGeometry();
            const material = new THREE.LineBasicMaterial({
                color: this.getStatusColor(satellite.data.status),
                transparent: true,
                opacity: 0.3
            });

            const line = new THREE.Line(geometry, material);
            this.connections.push({
                line: line,
                satellite: satellite,
                geometry: geometry
            });

            this.scene.add(line);
        });
    }

    setupLighting() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        this.scene.add(ambientLight);

        // Directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        directionalLight.castShadow = true;
        this.scene.add(directionalLight);

        // Point lights for dramatic effect
        const pointLight1 = new THREE.PointLight(0x6F4E37, 0.5, 20);
        pointLight1.position.set(0, 5, 0);
        this.scene.add(pointLight1);
    }

    setupControls() {
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.maxDistance = 30;
        this.controls.minDistance = 5;

        // Add mouse interaction
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();

        this.renderer.domElement.addEventListener('click', (event) => this.onMouseClick(event));
        this.renderer.domElement.addEventListener('mousemove', (event) => this.onMouseMove(event));
    }

    onMouseClick(event) {
        // Calculate mouse position in normalized device coordinates
        this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

        // Update the picking ray with the camera and mouse position
        this.raycaster.setFromCamera(this.mouse, this.camera);

        // Calculate objects intersecting the picking ray
        const clickableObjects = [...this.regions, ...this.satellites.map(s => s.mesh)];
        const intersects = this.raycaster.intersectObjects(clickableObjects);

        if (intersects.length > 0) {
            const clickedObject = intersects[0].object;
            this.handleObjectClick(clickedObject);
        }
    }

    onMouseMove(event) {
        // Calculate mouse position for hover effects
        this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

        this.raycaster.setFromCamera(this.mouse, this.camera);

        const hoverableObjects = [...this.regions, ...this.satellites.map(s => s.mesh)];
        const intersects = this.raycaster.intersectObjects(hoverableObjects);

        // Reset all hover states
        this.regions.forEach(region => {
            region.scale.setScalar(1);
        });
        this.satellites.forEach(satellite => {
            satellite.mesh.scale.setScalar(1);
        });

        // Apply hover effect to intersected object
        if (intersects.length > 0) {
            const hoveredObject = intersects[0].object;
            hoveredObject.scale.setScalar(1.2);
            this.renderer.domElement.style.cursor = 'pointer';
        } else {
            this.renderer.domElement.style.cursor = 'default';
        }
    }

    handleObjectClick(object) {
        if (object.userData.name) {
            // Clicked on a region
            this.updateInfoPanel({
                name: `${object.userData.name} Region`,
                type: 'region',
                status: object.userData.status
            });

            // Send message to Flutter
            if (window.FlutterChannel) {
                window.FlutterChannel.postMessage(`region_clicked:${object.userData.name}`);
            }

            // Create pulse effect from all satellites to this region
            this.satellites.forEach(satellite => {
                this.createPulse(satellite, object);
            });
        } else {
            // Clicked on a satellite
            const satellite = this.satellites.find(s => s.mesh === object);
            if (satellite) {
                this.updateInfoPanel(satellite.data);

                // Send message to Flutter
                if (window.FlutterChannel) {
                    window.FlutterChannel.postMessage(`satellite_clicked:${satellite.data.type}`);
                }

                // Create pulse to random region
                const randomRegion = this.regions[Math.floor(Math.random() * this.regions.length)];
                this.createPulse(satellite, randomRegion);
            }
        }
    }

    addGlowEffect(mesh, color) {
        const geometry = mesh.geometry.clone();
        const material = new THREE.MeshBasicMaterial({
            color: color,
            transparent: true,
            opacity: 0.2,
            side: THREE.BackSide
        });

        const glow = new THREE.Mesh(geometry, material);
        glow.scale.multiplyScalar(1.5);
        glow.position.copy(mesh.position);

        this.scene.add(glow);
    }

    getStatusColor(status) {
        switch (status) {
            case 'opportunity': return 0x4CAF50; // Green
            case 'watch': return 0xFFC107; // Yellow
            case 'threat': return 0xF44336; // Red
            default: return 0x6F4E37; // Coffee brown
        }
    }

    updateSatellitePositions() {
        this.satellites.forEach((satellite, index) => {
            const angle = satellite.data.angle + this.time * this.orbitSpeed;
            const x = Math.cos(angle) * this.orbitRadius;
            const z = Math.sin(angle) * this.orbitRadius;
            const y = Math.sin(this.time * 0.02 + index) * 0.5 + 2;

            satellite.group.position.set(x, y, z);

            // Rotate satellite
            satellite.mesh.rotation.y += 0.02;

            // Animate particles
            if (satellite.group.userData.particles) {
                satellite.group.userData.particles.rotation.y += 0.01;
            }
        });
    }

    updateConnections() {
        this.connections.forEach(connection => {
            const positions = [];

            // Start from satellite
            const satPos = connection.satellite.group.position;
            positions.push(satPos.x, satPos.y, satPos.z);

            // End at central node
            positions.push(0, 0, 0);

            connection.geometry.setAttribute(
                'position',
                new THREE.Float32BufferAttribute(positions, 3)
            );

            // Animate connection opacity based on data activity
            const opacity = 0.3 + Math.sin(this.time * 0.05) * 0.2;
            connection.line.material.opacity = opacity;
        });
    }

    createPulse(fromSatellite, toRegion) {
        // Create pulse effect when correlation is detected
        const geometry = new THREE.SphereGeometry(0.05, 8, 8);
        const material = new THREE.MeshBasicMaterial({
            color: 0xFFFFFF,
            transparent: true,
            opacity: 1
        });

        const pulse = new THREE.Mesh(geometry, material);
        pulse.position.copy(fromSatellite.group.position);

        this.scene.add(pulse);
        this.pulses.push({
            mesh: pulse,
            startPos: fromSatellite.group.position.clone(),
            endPos: toRegion.position.clone(),
            progress: 0
        });
    }

    updatePulses() {
        this.pulses.forEach((pulse, index) => {
            pulse.progress += 0.02;

            if (pulse.progress >= 1) {
                this.scene.remove(pulse.mesh);
                this.pulses.splice(index, 1);
                return;
            }

            // Interpolate position
            pulse.mesh.position.lerpVectors(
                pulse.startPos,
                pulse.endPos,
                pulse.progress
            );

            // Fade out
            pulse.mesh.material.opacity = 1 - pulse.progress;
            pulse.mesh.scale.setScalar(1 + pulse.progress * 2);
        });
    }

    simulateDataStreams() {
        // Simulate real-time data updates with more realistic patterns
        setInterval(() => {
            // Simulate coffee price correlation with weather
            if (Math.random() < 0.4) {
                const weatherSat = this.satellites.find(s => s.data.type === 'weather');
                const priceSat = this.satellites.find(s => s.data.type === 'prices');

                if (weatherSat && priceSat) {
                    // Weather affects prices - create correlation
                    this.createPulse(weatherSat, this.regions[0]);
                    setTimeout(() => {
                        this.createPulse(priceSat, this.regions[0]);
                        this.updateInfoPanel({
                            name: 'Correlation Detected',
                            type: 'correlation',
                            status: 'watch'
                        });
                    }, 1000);
                }
            }

            // Simulate disease outbreak spreading
            if (Math.random() < 0.2) {
                const diseaseSat = this.satellites.find(s => s.data.type === 'disease');
                if (diseaseSat) {
                    // Disease spreads to multiple regions
                    this.regions.forEach((region, index) => {
                        setTimeout(() => {
                            this.createPulse(diseaseSat, region);
                            region.material.color.setHex(0xF44336); // Red alert
                        }, index * 500);
                    });

                    this.updateInfoPanel({
                        name: 'Disease Alert',
                        type: 'disease',
                        status: 'threat'
                    });
                }
            }

            // Update satellite statuses with more realistic logic
            this.satellites.forEach(satellite => {
                if (Math.random() < 0.15) {
                    let newStatus;

                    // More realistic status changes based on type
                    switch (satellite.data.type) {
                        case 'prices':
                            newStatus = Math.random() < 0.6 ? 'threat' : 'watch';
                            break;
                        case 'weather':
                            newStatus = Math.random() < 0.4 ? 'threat' : 'opportunity';
                            break;
                        case 'disease':
                            newStatus = Math.random() < 0.7 ? 'threat' : 'watch';
                            break;
                        default:
                            const statuses = ['opportunity', 'watch', 'threat'];
                            newStatus = statuses[Math.floor(Math.random() * statuses.length)];
                    }

                    satellite.data.status = newStatus;

                    const newColor = this.getStatusColor(newStatus);
                    satellite.mesh.material.color.setHex(newColor);
                    satellite.mesh.material.emissive.setHex(newColor);

                    // Update connection line color
                    const connection = this.connections.find(c => c.satellite === satellite);
                    if (connection) {
                        connection.line.material.color.setHex(newColor);
                    }
                }
            });
        }, 2500);

        // Add periodic "intelligence bursts" - rapid fire correlations
        setInterval(() => {
            if (Math.random() < 0.3) {
                this.triggerIntelligenceBurst();
            }
        }, 8000);
    }

    triggerIntelligenceBurst() {
        // Rapid fire correlations showing AI analysis
        const burstCount = 3 + Math.floor(Math.random() * 3);

        for (let i = 0; i < burstCount; i++) {
            setTimeout(() => {
                const randomSat = this.satellites[Math.floor(Math.random() * this.satellites.length)];
                const randomRegion = this.regions[Math.floor(Math.random() * this.regions.length)];
                this.createPulse(randomSat, randomRegion);

                // Flash the central node
                this.centralNode.material.emissiveIntensity = 0.5;
                setTimeout(() => {
                    this.centralNode.material.emissiveIntensity = 0;
                }, 200);
            }, i * 300);
        }

        this.updateInfoPanel({
            name: 'AI Analysis',
            type: 'ai',
            status: 'opportunity'
        });
    }

    updateInfoPanel(satelliteData) {
        const panel = document.getElementById('data-streams');
        const statusClass = satelliteData.status;

        const messages = {
            prices: [
                'ICO prices down 12% - Brazil drought impact',
                'Arabica futures spike +8% on supply concerns',
                'Vietnam robusta exports delayed - opportunity window',
                'NY Coffee futures hit 3-month high',
                'Burundi premium grade +15% vs benchmark'
            ],
            weather: [
                'Satellite imagery: Heavy rains approaching Kayanza',
                'Drought conditions detected in Ngozi province',
                'Optimal harvest weather window: 5 days remaining',
                'Temperature anomaly: +3°C above seasonal average',
                'Rainfall 40% below normal - irrigation recommended'
            ],
            disease: [
                'Coffee leaf rust detected via drone surveillance',
                'Fungal spore count elevated in Muyinga region',
                'Berry borer infestation spreading from Tanzania',
                'Resistant variety adoption recommended',
                'Organic treatment effectiveness: 78% success rate'
            ],
            market: [
                'Bujumbura auction: Premium grade +22% price jump',
                'Export permits processed: 847 tons this week',
                'Quality scores trending upward: avg 84.5 points',
                'Direct trade inquiries from EU buyers +35%',
                'Cooperative membership growing: 1,247 new farmers'
            ],
            news: [
                'Government announces coffee sector investment plan',
                'New processing facility opens in Kayanza',
                'International buyers delegation arriving next week',
                'Coffee export tax reduced by 2% - profit boost',
                'Sustainable certification program launched'
            ],
            currency: [
                'BIF strengthening: Export profits up 8%',
                'USD/BIF rate favorable for next 30 days',
                'Central bank intervention stabilizing rates',
                'Remittance flows supporting currency',
                'Regional currency union talks progressing'
            ],
            correlation: [
                'AI detected: Weather pattern → Price volatility',
                'Correlation found: Disease outbreak → Market shift',
                'Pattern match: Brazil frost → Burundi opportunity',
                'Supply chain disruption → Premium pricing window',
                'Quality scores correlate with rainfall patterns'
            ],
            ai: [
                'AI Analysis: Optimal selling window in 3-5 days',
                'Machine learning: 87% confidence price increase',
                'Predictive model: Harvest timing critical',
                'Algorithm suggests: Focus on premium grades',
                'Intelligence synthesis: Multiple positive signals'
            ]
        };

        const messageArray = messages[satelliteData.type] || ['Data stream active'];
        const message = messageArray[Math.floor(Math.random() * messageArray.length)];

        const streamDiv = document.createElement('div');
        streamDiv.className = `data-stream ${statusClass}`;
        streamDiv.innerHTML = `<strong>${satelliteData.name}:</strong> ${message}`;

        // Add timestamp
        const timestamp = new Date().toLocaleTimeString();
        const timeSpan = document.createElement('span');
        timeSpan.style.float = 'right';
        timeSpan.style.fontSize = '10px';
        timeSpan.style.opacity = '0.7';
        timeSpan.textContent = timestamp;
        streamDiv.appendChild(timeSpan);

        panel.appendChild(streamDiv);

        // Keep only last 6 messages
        while (panel.children.length > 6) {
            panel.removeChild(panel.firstChild);
        }

        // Auto-scroll to latest message
        panel.scrollTop = panel.scrollHeight;
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        this.time += 0.016; // ~60fps

        // Update satellite positions
        this.updateSatellitePositions();

        // Update connections
        this.updateConnections();

        // Update pulses
        this.updatePulses();

        // Animate pulsing ring
        if (this.pulsingRing) {
            const scale = 1 + Math.sin(this.time * 2) * 0.1;
            this.pulsingRing.scale.set(scale, scale, scale);
        }

        // Update controls
        this.controls.update();

        // Render
        this.renderer.render(this.scene, this.camera);
    }

    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }
}

// Initialize the 3D visualization
document.addEventListener('DOMContentLoaded', () => {
    new AgriPulse3D();
});