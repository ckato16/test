    // --- Magenta Sound Player ---
    const player = new mm.SoundFontPlayer(
      'https://storage.googleapis.com/magentadata/js/soundfonts/sgm_plus'
    );

    const canvas = document.getElementById('visualizer');
    const ctx = canvas.getContext('2d');
    const scoreDisplay = document.getElementById('score');

    // Notes and pitches
    const noteToPitch = { C:60, D:62, E:64, F:65, G:67, A:69, B:71 };
    const noteOrder = ['C','D','E','F','G','A','B'];

    // Twinkle Twinkle melody
    const melody = ['C','C','G','G','A','A','G','F','F','E','E','D','D','C'];

    let score = 0;
    let keyRects = []; // clickable piano key areas

    // Create falling note objects
    const notes = melody.map((note, i) => ({
      note,
      pitch: noteToPitch[note],
      y: -i * 100,
      hit: false
    }));

    // --- Draw Piano ---
    function drawPiano() {
      const keyWidth = canvas.width / noteOrder.length;
      keyRects = [];
      noteOrder.forEach((n, i) => {
        const x = i * keyWidth;
        const y = canvas.height - 80;
        ctx.fillStyle = '#fff';
        ctx.fillRect(x, y, keyWidth, 80);
        ctx.strokeRect(x, y, keyWidth, 80);
        ctx.fillStyle = '#000';
        ctx.fillText(n, x + keyWidth / 2 - 4, canvas.height - 30);
        keyRects.push({ note: n, x, y, width: keyWidth, height: 80 });
      });
    }

    // --- Play a note ---
    function playPitch(pitch) {
      const seq = { notes: [{ pitch, startTime: 0, endTime: 0.3 }], totalTime: 0.3 };
      player.start(seq);
    }

    // --- Check if user hit correct falling note ---
    function checkHit(note) {
      const activeNote = notes.find(n => !n.hit && n.y > canvas.height - 150 && n.y < canvas.height - 60);
      if (activeNote && activeNote.note === note) {
        activeNote.hit = true;
        score++;
      }
    }

    // --- Keyboard input ---
    document.addEventListener('keydown', e => {
      const key = e.key.toUpperCase();
      if (!noteToPitch[key]) return;
      playPitch(noteToPitch[key]);
      checkHit(key);
    });

    // --- Mouse click on piano keys ---
    canvas.addEventListener('click', e => {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const key = keyRects.find(k =>
        x >= k.x && x <= k.x + k.width &&
        y >= k.y && y <= k.y + k.height
      );

      if (key) {
        playPitch(noteToPitch[key.note]);
        checkHit(key.note);
      }
    });

    // --- Animation loop ---
    function animate() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      drawPiano();

      const keyWidth = canvas.width / noteOrder.length;

      notes.forEach((n) => {
        const x = noteOrder.indexOf(n.note) * keyWidth;
        const y = n.y;
        ctx.fillStyle = n.hit ? 'lightgreen' : 'skyblue';
        ctx.fillRect(x + 5, y, keyWidth - 10, 20);
        n.y += 2;
      });

      scoreDisplay.textContent = `Score: ${score} / ${melody.length}`;

      const allDone = notes.every(n => n.y > canvas.height);
      if (!allDone) requestAnimationFrame(animate);
      else scoreDisplay.textContent += " ✅ Finished!";
    }

    animate();
