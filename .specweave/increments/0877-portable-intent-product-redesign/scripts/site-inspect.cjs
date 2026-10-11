const {chromium}=require('/tmp/specweave-0877-root/node_modules/@playwright/test');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8877/',{waitUntil:'networkidle'});
 await page.screenshot({path:'/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0877-portable-intent-product-redesign/reports/artifacts/specweave-desktop.png',fullPage:true});
 console.log(JSON.stringify({headings:await page.locator('h1,h2').allTextContents(),buttons:await page.getByRole('button').allTextContents(),overflow:await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),errors}));
 await page.setViewportSize({width:390,height:844});
 await page.screenshot({path:'/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0877-portable-intent-product-redesign/reports/artifacts/specweave-mobile.png',fullPage:true});
 console.log(JSON.stringify({mobileOverflow:await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),fonts:await page.locator('h1').evaluate(e=>getComputedStyle(e).fontFamily)}));
 await browser.close();
})();
