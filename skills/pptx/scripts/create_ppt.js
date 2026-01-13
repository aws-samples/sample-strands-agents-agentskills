const sharp = require('sharp');
const pptxgen = require('pptxgenjs');
const html2pptx = require('/home/ubuntu/workspace/strands-agentskills/skills/pptx/scripts/html2pptx.js');
const path = require('path');

async function createGradientBg() {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="562.5">
    <defs>
      <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#1a1a2e"/>
        <stop offset="50%" style="stop-color:#16213e"/>
        <stop offset="100%" style="stop-color:#0f3460"/>
      </linearGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#g)"/>
  </svg>`;

  await sharp(Buffer.from(svg))
    .png()
    .toFile('/home/ubuntu/workspace/strands-agentskills/_scratch/gradient-bg.png');
  
  return '/home/ubuntu/workspace/strands-agentskills/_scratch/gradient-bg.png';
}

async function createPresentation() {
  console.log('Creating gradient background...');
  const bgPath = await createGradientBg();

  console.log('Initializing presentation...');
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  pptx.author = 'Sales Analysis Team';
  pptx.title = 'Q1 2025 Sales Data Analysis';

  const basePath = '/home/ubuntu/workspace/strands-agentskills/_scratch';
  const outputPath = '/home/ubuntu/workspace/strands-agentskills/_output';

  // Update slide 1 HTML to use PNG background
  const slide1Html = `<!DOCTYPE html>
<html>
<head>
<style>
html { background: #1a1a2e; }
body {
  width: 720pt; height: 405pt; margin: 0; padding: 0;
  background-image: url('${bgPath}');
  background-size: cover;
  font-family: Arial, sans-serif;
  display: flex;
  align-items: center;
  justify-content: center;
}
.content {
  text-align: center;
  color: white;
}
h1 {
  font-size: 48pt;
  font-weight: bold;
  margin: 0 0 20pt 0;
  color: #ffffff;
}
.subtitle {
  font-size: 24pt;
  color: #e94560;
  margin: 0 0 40pt 0;
}
.date {
  font-size: 16pt;
  color: #a8dadc;
}
</style>
</head>
<body>
<div class="content">
  <h1>Sales Data Analysis</h1>
  <p class="subtitle">Q1 2025 Performance Report</p>
  <p class="date">January - March 2025</p>
</div>
</body>
</html>`;

  const fs = require('fs');
  fs.writeFileSync(`${basePath}/slide1_updated.html`, slide1Html);

  // Slide 1: Title
  console.log('Creating slide 1: Title');
  await html2pptx(`${basePath}/slide1_updated.html`, pptx);

  // Slide 2: Overview
  console.log('Creating slide 2: Overview');
  await html2pptx(`${basePath}/slide2_overview.html`, pptx);

  // Slide 3: Category Analysis
  console.log('Creating slide 3: Category Analysis');
  const { slide: slide3, placeholders: p3 } = await html2pptx(`${basePath}/slide3_category.html`, pptx);
  
  slide3.addImage({ 
    path: `${outputPath}/sales_by_category.png`, 
    x: p3[0].x, 
    y: p3[0].y, 
    w: p3[0].w, 
    h: p3[0].h 
  });

  // Slide 4: Monthly Trend
  console.log('Creating slide 4: Monthly Trend');
  const { slide: slide4, placeholders: p4 } = await html2pptx(`${basePath}/slide4_trend.html`, pptx);
  
  slide4.addImage({ 
    path: `${outputPath}/monthly_sales_trend.png`, 
    x: p4[0].x, 
    y: p4[0].y, 
    w: p4[0].w, 
    h: p4[0].h 
  });

  // Slide 5: Regional Performance
  console.log('Creating slide 5: Regional Performance');
  const { slide: slide5, placeholders: p5 } = await html2pptx(`${basePath}/slide5_region.html`, pptx);
  
  slide5.addImage({ 
    path: `${outputPath}/sales_by_region.png`, 
    x: p5[0].x, 
    y: p5[0].y, 
    w: p5[0].w, 
    h: p5[0].h 
  });

  slide5.addImage({ 
    path: `${outputPath}/sales_by_grade.png`, 
    x: p5[1].x, 
    y: p5[1].y, 
    w: p5[1].w, 
    h: p5[1].h 
  });

  // Slide 6: Top Products
  console.log('Creating slide 6: Top Products');
  const { slide: slide6, placeholders: p6 } = await html2pptx(`${basePath}/slide6_products.html`, pptx);
  
  slide6.addImage({ 
    path: `${outputPath}/top_products.png`, 
    x: p6[0].x, 
    y: p6[0].y, 
    w: p6[0].w, 
    h: p6[0].h 
  });

  // Slide 7: Conclusion
  console.log('Creating slide 7: Key Findings');
  await html2pptx(`${basePath}/slide7_conclusion.html`, pptx);

  // Save presentation
  console.log('Saving presentation...');
  await pptx.writeFile({ fileName: `${outputPath}/Sales_Analysis_Q1_2025.pptx` });
  
  console.log('✅ Presentation created successfully!');
  console.log(`Output: ${outputPath}/Sales_Analysis_Q1_2025.pptx`);
}

createPresentation().catch(err => {
  console.error('Error creating presentation:', err);
  process.exit(1);
});
