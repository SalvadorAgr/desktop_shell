
import sys

content = open('index.html').read()

# 1. Update variables and add cachedW/lastPaths
old_vars = """            let dockState = 'closed';
            let cachedW = 0, cachedH = 0;
            let lastDeltas = { fullD: '', leftD: '', rightD: '', taskD: '', splitX: -1, splitRatio: -1 };
            let isAnimating = false;"""

new_vars = """            let dockState = 'closed'; 
            let cachedW = 0, cachedH = 0;
            let lastPaths = { fullD: '', leftD: '', rightD: '', taskD: '', splitX: -1, splitRatio: -1 };
            let isLooping = false;
            let isDragging = false;
            let splitRatioAnimationActive = false;"""

# 2. Optimized Loop Logic
new_loop = """
            const startLoop = () => {
                if (!isLooping) {
                    isLooping = true;
                    requestAnimationFrame(animate);
                }
            };

            const animate = () => {
                const moving = updatePhysics(cachedH);
                updateGeometry();
                if (moving || splitRatioAnimationActive || isDragging) {
                    requestAnimationFrame(animate);
                } else {
                    isLooping = false;
                }
            };
"""

# Since string matching is hard, I will use a more robust regex or just replace the whole script if I can.
# But I don't want to break other things.

# Let's just try to overwrite the file with a clean version since I have the whole content from previous view_file.
