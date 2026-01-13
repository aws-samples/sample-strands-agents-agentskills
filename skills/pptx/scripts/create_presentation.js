const pptxgen = require('pptxgenjs');
const html2pptx = require('/home/ubuntu/workspace/strands-agentskills/skills/pptx/scripts/html2pptx.js');
const path = require('path');

const scratchDir = '/home/ubuntu/workspace/strands-agentskills/_scratch';
const outputDir = '/home/ubuntu/workspace/strands-agentskills/_output';

async function createPresentation() {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  pptx.author = 'Sales Analytics Team';
  pptx.title = 'Sales Data 분석 보고서 2025 Q1';

  // Slide 1: Title
  console.log('Creating slide 1: Title');
  await html2pptx(path.join(scratchDir, 'slide01.html'), pptx);

  // Slide 2: Key Summary
  console.log('Creating slide 2: Key Summary');
  await html2pptx(path.join(scratchDir, 'slide02.html'), pptx);

  // Slide 3: Monthly Sales Trend (3564 x 1764 = 2.02)
  console.log('Creating slide 3: Monthly Sales Trend');
  const { slide: slide3, placeholders: ph3 } = await html2pptx(path.join(scratchDir, 'slide03.html'), pptx);
  if (ph3.length > 0) {
    const aspectRatio = 3564 / 1764;
    const h = ph3[0].h;
    const w = h * aspectRatio;
    const x = ph3[0].x + (ph3[0].w - w) / 2;
    slide3.addImage({
      path: path.join(outputDir, '01_monthly_sales_trend.png'),
      x, y: ph3[0].y, w, h
    });
  }

  // Slide 4: Category Analysis (3946 x 1765 = 2.24)
  console.log('Creating slide 4: Category Analysis');
  const { slide: slide4, placeholders: ph4 } = await html2pptx(path.join(scratchDir, 'slide04.html'), pptx);
  if (ph4.length > 0) {
    const aspectRatio = 3946 / 1765;
    const h = ph4[0].h;
    const w = h * aspectRatio;
    const x = ph4[0].x + (ph4[0].w - w) / 2;
    slide4.addImage({
      path: path.join(outputDir, '02_category_analysis.png'),
      x, y: ph4[0].y, w, h
    });
  }

  // Slide 5: Regional Sales (3540 x 1764 = 2.01)
  console.log('Creating slide 5: Regional Sales');
  const { slide: slide5, placeholders: ph5 } = await html2pptx(path.join(scratchDir, 'slide05.html'), pptx);
  if (ph5.length > 0) {
    const aspectRatio = 3540 / 1764;
    const h = ph5[0].h;
    const w = h * aspectRatio;
    const x = ph5[0].x + (ph5[0].w - w) / 2;
    slide5.addImage({
      path: path.join(outputDir, '03_regional_sales.png'),
      x, y: ph5[0].y, w, h
    });
  }

  // Slide 6: Top Products (3542 x 2063 = 1.72)
  console.log('Creating slide 6: Top Products');
  const { slide: slide6, placeholders: ph6 } = await html2pptx(path.join(scratchDir, 'slide06.html'), pptx);
  if (ph6.length > 0) {
    const aspectRatio = 3542 / 2063;
    const h = ph6[0].h;
    const w = h * aspectRatio;
    const x = ph6[0].x + (ph6[0].w - w) / 2;
    slide6.addImage({
      path: path.join(outputDir, '04_top_products.png'),
      x, y: ph6[0].y, w, h
    });
  }

  // Slide 7: Customer Grade Analysis (4170 x 1765 = 2.36)
  console.log('Creating slide 7: Customer Grade Analysis');
  const { slide: slide7, placeholders: ph7 } = await html2pptx(path.join(scratchDir, 'slide07.html'), pptx);
  if (ph7.length > 0) {
    const aspectRatio = 4170 / 1765;
    const h = ph7[0].h;
    const w = h * aspectRatio;
    const x = ph7[0].x + (ph7[0].w - w) / 2;
    slide7.addImage({
      path: path.join(outputDir, '05_customer_grade_analysis.png'),
      x, y: ph7[0].y, w, h
    });
  }

  // Slide 8: Daily Sales Trend (4163 x 1765 = 2.36)
  console.log('Creating slide 8: Daily Sales Trend');
  const { slide: slide8, placeholders: ph8 } = await html2pptx(path.join(scratchDir, 'slide08.html'), pptx);
  if (ph8.length > 0) {
    const aspectRatio = 4163 / 1765;
    const h = ph8[0].h;
    const w = h * aspectRatio;
    const x = ph8[0].x + (ph8[0].w - w) / 2;
    slide8.addImage({
      path: path.join(outputDir, '06_daily_sales_trend.png'),
      x, y: ph8[0].y, w, h
    });
  }

  // Slide 9: Region-Category Heatmap (2765 x 1764 = 1.57)
  console.log('Creating slide 9: Region-Category Heatmap');
  const { slide: slide9, placeholders: ph9 } = await html2pptx(path.join(scratchDir, 'slide09.html'), pptx);
  if (ph9.length > 0) {
    const aspectRatio = 2765 / 1764;
    const h = ph9[0].h;
    const w = h * aspectRatio;
    const x = ph9[0].x + (ph9[0].w - w) / 2;
    slide9.addImage({
      path: path.join(outputDir, '07_region_category_heatmap.png'),
      x, y: ph9[0].y, w, h
    });
  }

  // Slide 10: Dashboard Overview (3920 x 2838 = 1.38)
  console.log('Creating slide 10: Dashboard Overview');
  const { slide: slide10, placeholders: ph10 } = await html2pptx(path.join(scratchDir, 'slide10.html'), pptx);
  if (ph10.length > 0) {
    const aspectRatio = 3920 / 2838;
    const h = ph10[0].h;
    const w = h * aspectRatio;
    const x = ph10[0].x + (ph10[0].w - w) / 2;
    slide10.addImage({
      path: path.join(outputDir, '08_dashboard_overview.png'),
      x, y: ph10[0].y, w, h
    });
  }

  // Slide 11: Strategic Recommendations
  console.log('Creating slide 11: Strategic Recommendations');
  await html2pptx(path.join(scratchDir, 'slide11.html'), pptx);

  // Save presentation
  const outputPath = path.join(outputDir, 'sales_analysis_report.pptx');
  await pptx.writeFile({ fileName: outputPath });
  console.log(`Presentation saved successfully: ${outputPath}`);
}

createPresentation().catch(console.error);
