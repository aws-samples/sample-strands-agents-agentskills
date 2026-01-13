const pptxgen = require('pptxgenjs');
const html2pptx = require('./html2pptx');
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const scratchDir = path.join(__dirname, '../../../_scratch');
const outputDir = path.join(__dirname, '../../../_output');

async function createGradientBackground() {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="810">
    <defs>
      <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#1C2833"/>
        <stop offset="100%" style="stop-color:#2E4053"/>
      </linearGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#g)"/>
  </svg>`;
  
  const bgPath = path.join(scratchDir, 'gradient-bg.png');
  await sharp(Buffer.from(svg))
    .png()
    .toFile(bgPath);
  
  return bgPath;
}

async function createPresentation() {
  console.log('Creating gradient background...');
  const bgPath = await createGradientBackground();
  
  // Update slide1.html to use the PNG background
  const slide1Path = path.join(scratchDir, 'slide1.html');
  const slide1Html = fs.readFileSync(slide1Path, 'utf8');
  const updatedSlide1 = slide1Html.replace(
    'background: linear-gradient(135deg, #1C2833 0%, #2E4053 100%);',
    `background-image: url('${bgPath}'); background-size: cover;`
  );
  fs.writeFileSync(slide1Path, updatedSlide1);
  
  console.log('Creating presentation...');
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  pptx.author = 'Sales Analysis Team';
  pptx.title = '2025 Q1 판매 분석 보고서';
  
  // Read analysis data
  const analysisPath = path.join(scratchDir, 'sales_analysis.json');
  const analysis = JSON.parse(fs.readFileSync(analysisPath, 'utf8'));
  
  // Slide 1: Title
  console.log('  Adding slide 1...');
  await html2pptx(slide1Path, pptx);
  
  // Slide 2: Key Metrics
  console.log('  Adding slide 2...');
  await html2pptx(path.join(scratchDir, 'slide2.html'), pptx);
  
  // Slide 3: Category Sales
  console.log('  Adding slide 3...');
  const { slide: slide3, placeholders: p3 } = await html2pptx(path.join(scratchDir, 'slide3.html'), pptx);
  
  slide3.addChart(pptx.charts.PIE, [{
    name: "카테고리별 매출",
    labels: Object.keys(analysis.by_category),
    values: Object.values(analysis.by_category).map(c => c.sales)
  }], {
    ...p3[0],
    showPercent: true,
    showLegend: true,
    legendPos: 'r',
    chartColors: ["5EA8A7", "2E4053"]
  });
  
  // Slide 4: Regional Sales
  console.log('  Adding slide 4...');
  const { slide: slide4, placeholders: p4 } = await html2pptx(path.join(scratchDir, 'slide4.html'), pptx);
  
  const regions = Object.keys(analysis.by_region);
  const regionSales = regions.map(r => analysis.by_region[r].sales);
  
  slide4.addChart(pptx.charts.BAR, [{
    name: "지역별 매출",
    labels: regions,
    values: regionSales
  }], {
    ...p4[0],
    barDir: 'bar',
    showTitle: false,
    showLegend: false,
    showCatAxisTitle: true,
    catAxisTitle: '지역',
    showValAxisTitle: true,
    valAxisTitle: '매출 (백만원)',
    valAxisMinVal: 0,
    valAxisMaxVal: 25000000,
    valAxisMajorUnit: 5000000,
    chartColors: ["5EA8A7"]
  });
  
  // Slide 5: Customer Grade
  console.log('  Adding slide 5...');
  const { slide: slide5, placeholders: p5 } = await html2pptx(path.join(scratchDir, 'slide5.html'), pptx);
  
  const grades = ['VIP', '우수', '일반'];
  const gradeSales = grades.map(g => analysis.by_grade[g].sales);
  
  slide5.addChart(pptx.charts.BAR, [{
    name: "고객등급별 매출",
    labels: grades,
    values: gradeSales
  }], {
    ...p5[0],
    barDir: 'col',
    showTitle: false,
    showLegend: false,
    showCatAxisTitle: true,
    catAxisTitle: '고객등급',
    showValAxisTitle: true,
    valAxisTitle: '매출 (백만원)',
    valAxisMinVal: 0,
    valAxisMaxVal: 50000000,
    valAxisMajorUnit: 10000000,
    chartColors: ["5EA8A7"]
  });
  
  // Slide 6: Monthly Trend
  console.log('  Adding slide 6...');
  const { slide: slide6, placeholders: p6 } = await html2pptx(path.join(scratchDir, 'slide6.html'), pptx);
  
  const months = Object.keys(analysis.monthly_trend);
  const monthlySales = Object.values(analysis.monthly_trend);
  const monthLabels = months.map(m => m.substring(5) + '월');
  
  slide6.addChart(pptx.charts.LINE, [{
    name: "월별 매출",
    labels: monthLabels,
    values: monthlySales
  }], {
    ...p6[0],
    lineSize: 4,
    lineSmooth: true,
    showTitle: false,
    showLegend: false,
    showCatAxisTitle: true,
    catAxisTitle: '월',
    showValAxisTitle: true,
    valAxisTitle: '매출 (백만원)',
    valAxisMinVal: 0,
    valAxisMaxVal: 30000000,
    valAxisMajorUnit: 10000000,
    chartColors: ["5EA8A7"]
  });
  
  // Save presentation
  console.log('Saving presentation...');
  const outputPath = path.join(outputDir, 'sales_analysis.pptx');
  await pptx.writeFile({ fileName: outputPath });
  console.log('✅ Presentation created: _output/sales_analysis.pptx');
}

createPresentation().catch(err => {
  console.error('❌ Error creating presentation:', err);
  process.exit(1);
});
