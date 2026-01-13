const sharp = require('sharp');

async function createGradient() {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="562.5">
    <defs>
      <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#2C3E50"/>
        <stop offset="100%" style="stop-color:#3498DB"/>
      </linearGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#g)"/>
  </svg>`;

  await sharp(Buffer.from(svg))
    .png()
    .toFile('/tmp/gradient-bg.png');
  
  console.log('Gradient created');
}

createGradient().catch(console.error);
