const sharp = require('sharp');

async function getImageSize(path) {
  const metadata = await sharp(path).metadata();
  return { width: metadata.width, height: metadata.height };
}

(async () => {
  const img1 = await getImageSize('/home/ubuntu/workspace/strands-agentskills/sales_analysis_dashboard.png');
  const img2 = await getImageSize('/home/ubuntu/workspace/strands-agentskills/sales_trends_detailed.png');
  console.log('sales_analysis_dashboard.png:', img1);
  console.log('sales_trends_detailed.png:', img2);
})();
