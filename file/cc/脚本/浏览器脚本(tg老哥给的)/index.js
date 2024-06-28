require('events').EventEmitter.defaultMaxListeners = 0;
const puppeteer = require('puppeteer-extra')
const RecaptchaPlugin = require('puppeteer-extra-plugin-recaptcha');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');


function solving(message) {
    return new Promise((resolve, reject) => {
		
		console.log(`[BROWSER] Proxy ${message.proxy}`) 
        console.log(`[BROWSER] Launch browser...`)
        console.log(`[BROWSER] Target: ${message.url}`)		
		
        puppeteer.use(StealthPlugin())
        puppeteer.use(RecaptchaPlugin({
            provider: {
                id: '2captcha',
                token: '484f6867edd89ad23af2d4cdfae8cbf5'
            },
            visualFeedback: true
        }))
        puppeteer.launch({
            headless: true,
            ignoreHTTPSErrors: true,
            ignoreDefaultArgs: [
                "--disable-extensions",
                "--enable-automation"
            ],
            args: [
                `--proxy-server=http://${message.proxy}`,
                '--disable-features=IsolateOrigins,site-per-process,SitePerProcess',
                '--flag-switches-begin --disable-site-isolation-trials --flag-switches-end',
                `--window-size=1920,1080`,
                "--window-position=000,000",
                "--disable-dev-shm-usage",
				'--user-agent=' + message.user_agent,
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--hide-scrollbars',
                '--mute-audio',
                '--disable-gl-drawing-for-tests',
                '--disable-canvas-aa',
                '--disable-2d-canvas-clip-aa',
                '--disable-web-security',
                '--ignore-certificate-errors',
                '--ignore-certificate-errors-spki-list',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
        }).then(async (browser) => {

            try {
                const page = await browser.newPage()
                await page.setJavaScriptEnabled(true);
                await page.setDefaultNavigationTimeout(60000);
                await page.evaluateOnNewDocument(() => {
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false
                    });
                })
                await page.evaluateOnNewDocument(() => {
                    Object.defineProperty(navigator, 'platform', {
                        get: () => 'Win32'
                    });
                })
               try {
                    const headeri = await page.on('request', req => {
                        const headers = req.headers();
                        headers['authority'] = `${message.host}`;
						headers['method'] = `${message.mode}`;
						headers['scheme'] = 'https';
                        headers['upgrade-insecure-requests'] = '1';
                        headers['sec-fetch-site'] = 'same-origin';
                        headers['sec-fetch-user'] = '?1';
                        headers['sec-Fetch-mode'] = 'navigate';
                        headers['sec-Fetch-dest'] = 'document';
                        headers['sec-ch-ua-platform'] = '"Windows"';
                        headers['sec-ch-ua-mobile'] = '?0';
                        headers['accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9';
                        headers['accept-language'] = 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7';
                        headers['accept-encoding'] = 'gzip, deflate, br';
                        headers['sec-gpc'] = '1';
                        headers['cache-control'] = 'no-cache';
                        headers['pragma'] = 'no-cache';
                    });
                    const admv = await page.goto(message.url)
					page.on('dialog', async dialog => {
						await dialog.accept();
					});
					const checkstatus = await admv.status();
					console.log(`[BROWSER] Status code: [${checkstatus}]`);	
					if (checkstatus == "200")
					{
						const ifdvestitovivod = (await page.title()).toString().trim();
						const cookies = await page.cookies()
						if (cookies) {					
							resolve(cookies);
							console.log('[BROWSER] Title: ' + ifdvestitovivod + ' ');
							browser.close();
							return;
						}
					}	
					
					if (checkstatus == "503") {
						console.log(`[BROWSER] Detected protection`);
						console.log(`[BROWSER] [10] secound`)								
					}
					
					if (checkstatus == "520") {
						console.log(`[BROWSER] Maybe api block | BROWSER RELOAD`);	
						browser.close();
					}
					
					if (checkstatus == "429")
					{
						if (reqperip >= 2)
						{
							reqperip = -1;
							browser.close();
						}
					}	
					
					if (checkstatus == "407")
					{
						browser.close();
					}
					
					if(message.baloo == "true") {
						if (checkstatus == "403")
						{
							browser.close();
						}
					}					
					
					const checkblock = await page.title();
					if (checkblock == "Access denied") {
						console.log('[BROWSER] Access denied: [1020] | BROWSER RELOAD');
						browser.close();
					}	

					await page.waitForTimeout(10000, { waitUntil:'networkidle0' })
					
                } catch (error) {
                    await browser.close();
                }
                try {
						await page.waitForTimeout(8000, { waitUntil:'networkidle0' })	
						const maybeuam = await page.$('#cf-wrapper');
						if (maybeuam)
						{
							try {
								await page.waitForNavigation({waitUntil: 'domcontentloaded', timeout: 9500});
								console.log(`[BROWSER] Selector: found, [9.5] secound`)		
							} catch(errorbypasuam) {
								console.log(`[BROWSER] No bypass cloudflare uam.`)
								reject(errorbypasuam)
								await browser.close();
							}								
						}		

						const checkcf = await page.$('#challenge-running');
						if (checkcf) {
							try { 
								await page.waitForNavigation({waitUntil: 'domcontentloaded', timeout: 9500});
								console.log(`[BROWSER] [9.5] secound [bypass cloudflare uam]`)	
							} catch(errorbpuamcf) {
								console.log(`[BROWSER] No bypass cloudflare uam.`)
								reject(errorbpuamcf)
								await browser.close();								
							}
						}						

						const maybecaptchav1 = await page.$('#h-captcha');
						if (maybecaptchav1)
						{
							console.log(`[BROWSER] Found hcaptcha, bypassing... | [v1]`)
							await page.waitForSelector('#h-captcha');
							await page.solveRecaptchas()
							try {
								console.log(`[BROWSER] Try bypass hcaptcha... | [v1]`)	
								await page.waitForNavigation({waitUntil: 'domcontentloaded', timeout: 25000});
							} catch (eds) {
								console.log(`[BROWSER] No bypass hcaptcha [v1]`)
								reject(eds)
								await browser.close();
							}						
						}

						const maybecaptchav2 = await page.$('#cf-hcaptcha-container');
						if (maybecaptchav2)
						{
							console.log(`[BROWSER] Found hcaptcha, bypassing... | [v2]`)
							await page.waitForSelector('#cf-hcaptcha-container');
							await page.solveRecaptchas()
							try {
								console.log(`[BROWSER] Try bypass hcaptcha... | [v2]`)	
								await page.waitForNavigation({waitUntil: 'domcontentloaded', timeout: 25000});
							} catch (abs) {
								console.log(`[BROWSER] No bypass hcaptcha [v2]`)
								reject(abs)
								await browser.close();
							}								
						}

						const mayberecaptchav1 = await page.$('#recaptcha');
						if (mayberecaptchav1)
						{
							console.log(`[BROWSER] Found recaptcha, bypassing... | [v1]`)
							await page.waitForSelector('#recaptcha');
							await page.solveRecaptchas()
							try {
								console.log(`[BROWSER] Try bypass recaptcha... | [v1]`)	
								await page.waitForNavigation({waitUntil: 'domcontentloaded', timeout: 25000});
							} catch (abs) {
								console.log(`[BROWSER] No bypass recaptcha [v1]`)
								reject(abs)
								await browser.close();
							}								
						}

					const checkblockv2 = await page.title();
					if (checkblockv2 == "Just a moment...") {
						console.log('[BROWSER] NO BYPASS: [403] | BROWSER RELOAD');
						browser.close();
					}	

					if (checkblockv2 == "DDOS-GUARD") {
						console.log('[BROWSER] NO BYPASS: [403] | BROWSER RELOAD');
						browser.close();
					}

					if (checkblockv2 == "Cloudflare is checking your browser...") {
						console.log('[BROWSER] NO BYPASS: [403] | BROWSER RELOAD');
						browser.close();
					}										
						
					const pagestitle = (await page.title()).toString().trim();
                    const cookies = await page.cookies()
                    if (cookies) {					
                        resolve(cookies);
						console.log('[BROWSER] Title: ' + pagestitle + ' ');
                        await browser.close();
                        return;
                    }
                } catch (ee) {
                    reject(ee)
                    await browser.close();
                }

            } catch (e) {
            }

        })
    })
}

module.exports = {
    solving: solving
}