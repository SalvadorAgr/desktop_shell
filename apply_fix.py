
import sys

with open('index.html', 'r') as f:
    lines = f.readlines()

new_script_content = r"""
            const container = document.getElementById('main-container');
            const trigger = document.getElementById('panel-trigger');
            const splitTrigger = document.getElementById('splitview-trigger');
            const maskFull = document.getElementById('mask-full');
            const leftPaneMask = document.getElementById('pane-left-mask-path');
            const rightPaneMask = document.getElementById('pane-right-mask-path');
            const canvasPath = document.getElementById('main-canvas-path');
            const dockElements = document.getElementById('dock-elements');
            const splitDivider = document.getElementById('splitview-divider');
            const wrapper = container.querySelector('.main-canvas-wrapper');
            const taskPanelPath = document.getElementById('task-panel-path');
            const overlaySvg = document.querySelector('.canvas-overlay-svg');
            const panesContainer = document.querySelector('.panes-container');
            const maskSplitGroup = document.getElementById('mask-split-group');
            const zipperRectSplit = document.getElementById('zipper-rect-split');
            const zipperRectFull = document.getElementById('zipper-rect-full');

            let splitRatio = 1.0; 
            let viewMode = 'single-left'; 

            let dockState = 'closed'; 
            let cachedW = 0, cachedH = 0;
            let lastPaths = { fullD: '', leftD: '', rightD: '', taskD: '', splitX: -1, splitRatio: -1 };
            let isLooping = false;
            let isDragging = false;
            let splitRatioAnimationActive = false;

            const K_CENTER = 0.05;
            const K_LATERAL = 0.025;
            const DAMPING = 0.35;
            const DT = 1.0;

            const particles = {
                dL: { x: 0, y: 700, py: 700, k: K_LATERAL, ty: 0 },
                dR: { x: 0, y: 700, py: 700, k: K_LATERAL, ty: 0 },
                dC1: { x: 0, y: 700, py: 700, k: K_LATERAL * 1.5, ty: 0 },
                dC2: { x: 0, y: 700, py: 700, k: K_CENTER, ty: 0 },
                dC3: { x: 0, y: 700, py: 700, k: K_CENTER, ty: 0 },
                dC4: { x: 0, y: 700, py: 700, k: K_LATERAL * 1.5, ty: 0 }
            };

            const initParticles = (w, h) => {
                cachedW = w; cachedH = h;
                const bottom = h - 1;
                const dockTop = h - 26;
                particles.dL.y = particles.dL.py = bottom; particles.dL.ty = bottom;
                particles.dR.y = particles.dR.py = bottom; particles.dR.ty = bottom;
                particles.dC1.y = particles.dC1.py = bottom; particles.dC1.ty = bottom;
                particles.dC2.y = particles.dC2.py = bottom; particles.dC2.ty = dockTop;
                particles.dC3.y = particles.dC3.py = bottom; particles.dC3.ty = dockTop;
                particles.dC4.y = particles.dC4.py = bottom; particles.dC4.ty = bottom;
                startLoop();
            };

            const updatePhysics = (h) => {
                if (!h) return false;
                const bottom = h - 1;
                const isClosed = (dockState === 'closed');
                let moving = false;
                const progress = (bottom - particles.dC2.y) / 25;
                const centerVis = Math.max(0, (progress - 0.82) / 0.18);
                const edgeVis = Math.max(0, (progress - 0.95) / 0.05);
                const icons = dockElements.querySelectorAll('.dock-icon');
                const lines = dockElements.querySelectorAll('line');
                icons.forEach((icon, idx) => {
                    const isCenter = (idx === 1);
                    const v = isCenter ? centerVis : edgeVis;
                    icon.style.opacity = Math.pow(v, 2);
                    icon.style.pointerEvents = (v > 0.5) ? 'auto' : 'none';
                });
                lines.forEach(line => { line.style.opacity = Math.pow(edgeVis, 2); });
                for (let key in particles) {
                    const p = particles[key];
                    const targetY = isClosed ? bottom : p.ty;
                    const force = (targetY - p.y) * p.k;
                    const velocity = (p.y - p.py) * DAMPING;
                    const nextY = p.y + velocity + force * (DT * DT);
                    if (Math.abs(nextY - p.y) > 0.001 || Math.abs(targetY - nextY) > 0.001) moving = true;
                    p.py = p.y; p.y = nextY;
                }
                return moving;
            };

            const updateGeometry = () => {
                const w = cachedW; const h = cachedH;
                if (!w || !h) return;
                const svg = canvasPath.closest('svg');
                const viewBoxStr = `0 0 ${w} ${h}`;
                if (svg.getAttribute('viewBox') !== viewBoxStr) {
                    svg.setAttribute('viewBox', viewBoxStr);
                    overlaySvg.setAttribute('viewBox', viewBoxStr);
                }
                const L = 0, R = w, rad = 10, bottom = h - 1;
                let splitX = Math.round(w * splitRatio);
                splitX = Math.max(0, Math.min(w, splitX));
                const p = particles; const dockCenter = Math.round(w / 2);
                p.dL.x = dockCenter - 121; p.dR.x = dockCenter + 119;
                p.dC1.x = dockCenter - 96; p.dC2.x = dockCenter - 71;
                p.dC3.x = dockCenter + 69; p.dC4.x = dockCenter + 94;
                const fullD = `M ${L + rad} 1 H ${R - rad} Q ${R} 1 ${R} ${1 + rad} V ${bottom - rad} Q ${R} ${bottom} ${R - rad} ${bottom} H ${p.dR.x} C ${p.dC4.x} ${bottom} ${p.dC4.x} ${p.dC3.y} ${p.dC3.x} ${p.dC3.y} H ${p.dC2.x} C ${p.dC1.x} ${p.dC2.y} ${p.dC1.x} ${bottom} ${p.dL.x} ${bottom} H ${L + rad} Q ${L} ${bottom} ${L} ${bottom - rad} V ${1 + rad} Q ${L} 1 ${L + rad} 1 Z`;
                const leftD = `M ${L + rad} 1 H ${splitX - 2 - rad} Q ${splitX - 2} 1 ${splitX - 2} ${1 + rad} V ${p.dC2.y} H ${p.dC2.x} C ${p.dC1.x} ${p.dC2.y} ${p.dC1.x} ${bottom} ${p.dL.x} ${bottom} H ${L + rad} Q ${L} ${bottom} ${L} ${bottom - rad} V ${1 + rad} Q ${L} 1 ${L + rad} 1 Z`;
                const rightD = `M ${splitX + 2 + rad} 1 H ${R - rad} Q ${R} 1 ${R} ${1 + rad} V ${bottom - rad} Q ${R} ${bottom} ${R - rad} ${bottom} H ${p.dR.x} C ${p.dC4.x} ${bottom} ${p.dC4.x} ${p.dC3.y} ${p.dC3.x} ${p.dC3.y} H ${splitX + 2} V ${1 + rad} Q ${splitX + 2} 1 ${splitX + 2 + rad} 1 Z`;
                if (fullD !== lastPaths.fullD) { canvasPath.setAttribute('d', fullD); maskFull.setAttribute('d', fullD); lastPaths.fullD = fullD; }
                if (leftD !== lastPaths.leftD) { leftPaneMask.setAttribute('d', leftD); lastPaths.leftD = leftD; }
                if (rightD !== lastPaths.rightD) { rightPaneMask.setAttribute('d', rightD); lastPaths.rightD = rightD; }
                const taskWrapper = container.querySelector('.task-panel-wrapper');
                if (taskWrapper.offsetWidth > 1) {
                    const taskH = taskWrapper.offsetHeight || 663;
                    const taskW = 300, taskRad = 10, taskBottom = taskH - 1;
                    const taskD = `M 0 ${taskBottom - taskRad} V ${taskRad} Q 0 1 ${taskRad} 1 H ${taskW - taskRad} Q ${taskW} 1 ${taskW} ${taskRad} V ${taskBottom - taskRad} Q ${taskW} ${taskBottom} ${taskW - taskRad} ${taskBottom} H ${taskRad} Q 0 ${taskBottom} 0 ${taskBottom - taskRad} Z`;
                    if (taskPanelPath && taskD !== lastPaths.taskD) { taskPanelPath.setAttribute('d', taskD); lastPaths.taskD = taskD; }
                }
                dockElements.setAttribute('transform', `translate(${dockCenter - 618}, ${h - 656.5})`);
                splitDivider.style.transform = `translate(${splitX - 2}px, 0)`;
                if (splitRatio !== lastPaths.splitRatio || splitX !== lastPaths.splitX) {
                    if (splitRatio >= 0.99) { panesContainer.style.gridTemplateColumns = `1fr 0px 0px`; splitDivider.style.display = 'none'; }
                    else if (splitRatio <= 0.01) { panesContainer.style.gridTemplateColumns = `0px 0px 1fr`; splitDivider.style.display = 'none'; }
                    else { panesContainer.style.gridTemplateColumns = `${splitX - 2}px 4px ${w - splitX - 2}px`; splitDivider.style.display = 'block'; }
                    const maskFullGrp = document.getElementById('mask-full-group');
                    const maskSplitGrp = document.getElementById('mask-split-group');
                    if (splitRatio > 0.99 || splitRatio < 0.01) { maskFullGrp.style.display = 'block'; maskSplitGrp.style.display = 'none'; }
                    else { maskFullGrp.style.display = 'none'; maskSplitGrp.style.display = 'block'; }
                    lastPaths.splitRatio = splitRatio; lastPaths.splitX = splitX;
                }
                zipperRectSplit.setAttribute('height', '100%'); zipperRectFull.setAttribute('height', '100%');
                zipperRectFull.setAttribute('y', '0'); canvasPath.setAttribute('mask', 'url(#split-mask)');
            };

            const animate = () => {
                const moving = updatePhysics(cachedH);
                updateGeometry();
                if (moving || splitRatioAnimationActive || isDragging) { requestAnimationFrame(animate); }
                else { isLooping = false; }
            };

            const startLoop = () => { if (!isLooping) { isLooping = true; requestAnimationFrame(animate); } };

            const onResize = () => {
                cachedW = wrapper.offsetWidth; cachedH = wrapper.offsetHeight;
                updateGeometry(); startLoop();
            };
            const rObs = new ResizeObserver(onResize);
            rObs.observe(wrapper); rObs.observe(container.querySelector('.task-panel-wrapper'));

            const hitArea = document.getElementById('dock-hit-area');
            const backdrop = document.getElementById('dock-backdrop');
            hitArea.addEventListener('mouseenter', () => {
                if (dockState === 'closed') {
                    dockState = 'open'; hitArea.style.pointerEvents = 'none';
                    backdrop.style.display = 'block'; startLoop();
                }
            });

            backdrop.addEventListener('mousedown', () => {
                dockState = 'closed'; backdrop.style.display = 'none';
                setTimeout(() => { hitArea.style.pointerEvents = 'auto'; }, 500);
                startLoop();
            });

            window.addEventListener('load', () => {
                cachedW = wrapper.offsetWidth; cachedH = wrapper.offsetHeight;
                initParticles(cachedW, cachedH);
                populateAppGrid();
            });

            const apps = [
                { name: 'Gmail', file: 'gmail.svg', url: 'https://mail.google.com' },
                { name: 'Google', file: 'google.svg', url: 'https://google.com' },
                { name: 'WhatsApp', file: 'Whatsapp.svg', url: 'https://web.whatsapp.com' },
                { name: 'Drive', file: 'drive.svg', url: 'https://drive.google.com' },
                { name: 'Add', file: 'añadir.svg', url: 'action:add' }
            ];

            const populateAppGrid = () => {
                const grid = document.createElement('div');
                grid.className = 'app-grid';
                apps.forEach(app => {
                    const img = document.createElement('img');
                    img.src = `assets/svg/panel_apps/iconos_app/${app.file}`;
                    img.className = 'app-icon'; img.alt = app.name;
                    img.addEventListener('click', () => {
                        if (app.url === 'action:add') console.log('Open Add Modal');
                        else openUrlInSplit(app.url);
                    });
                    grid.appendChild(img);
                });
                document.querySelector('.task-panel-wrapper').appendChild(grid);
            };

            const openUrlInSplit = (url) => {
                splitRatio = 0.5; if (dockState === 'closed') dockState = 'open';
                const rightPane = document.getElementById('pane-right');
                rightPane.innerHTML = `<webview id="wv-right" src="${url}" style="width:100%; height:100%;" allowpopups></webview>`;
                container.classList.add('splitview-active');
                startLoop();
            };

            const animateSplitRatio = (targetRatio) => {
                splitRatioAnimationActive = true;
                const duration = 500; const startTime = performance.now();
                const startRatio = splitRatio;
                startLoop();
                const step = (now) => {
                    const elapsed = now - startTime;
                    const p = Math.min(elapsed / duration, 1);
                    const ease = 1 - Math.pow(1 - p, 3);
                    splitRatio = startRatio + (targetRatio - startRatio) * ease;
                    if (p < 1) requestAnimationFrame(step);
                    else {
                        splitRatio = targetRatio; splitRatioAnimationActive = false;
                        updateViewModeState();
                    }
                };
                requestAnimationFrame(step);
            };

            const updateViewModeState = () => {
                if (splitRatio >= 0.99) { viewMode = 'single-left'; container.classList.remove('splitview-active'); }
                else if (splitRatio <= 0.01) { viewMode = 'single-right'; container.classList.remove('splitview-active'); }
                else { viewMode = 'split'; container.classList.add('splitview-active'); }
            };

            const onMouseMove = (e) => {
                if (!isDragging) return;
                const rect = wrapper.getBoundingClientRect();
                let x = e.clientX - rect.left;
                if (x < 30) x = 0; if (x > rect.width - 30) x = rect.width;
                splitRatio = x / rect.width;
            };

            const onMouseUp = () => {
                isDragging = false; document.body.classList.remove('is-resizing');
                window.removeEventListener('mousemove', onMouseMove);
                window.removeEventListener('mouseup', onMouseUp);
                updateViewModeState(); startLoop();
            };

            splitDivider.addEventListener('mousedown', (e) => {
                isDragging = true; document.body.classList.add('is-resizing');
                window.addEventListener('mousemove', onMouseMove);
                window.addEventListener('mouseup', onMouseUp);
                startLoop(); e.preventDefault();
            });

            const wvLeft = document.getElementById('wv-left');
            wvLeft.addEventListener('did-finish-load', () => console.log('Main webview loaded'));
"""

# Reconstruct everything between <script> and </script>
start_tag = "<script>"
end_tag = "</script>"

new_lines = []
in_script = False
for line in lines:
    if start_tag in line:
        new_lines.append(line)
        new_lines.append(new_script_content + "\n")
        in_script = True
    elif end_tag in line:
        new_lines.append(line)
        in_script = False
    elif not in_script:
        new_lines.append(line)

with open('index.html', 'w') as f:
    f.writelines(new_lines)
