package main

import (
	"bufio"
	"crypto/tls"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"
)

// Proxy 结构体，用于存储代理的IP和端口
type Proxy struct {
	IP   string
	Port string
}

// 自定义Transport来忽略无效的响应
type customTransport struct {
	transport http.RoundTripper
}

// RoundTrip方法实现自定义的HTTP请求处理逻辑
func (t *customTransport) RoundTrip(req *http.Request) (*http.Response, error) {
	resp, err := t.transport.RoundTrip(req)
	if err != nil {
		return resp, err
	}
	if resp.StatusCode == http.StatusSwitchingProtocols {
		resp.Body.Close()
		return nil, fmt.Errorf("invalid response")
	}
	return resp, err
}

// 禁用日志输出
func disableLogging() {
	log.SetFlags(0)
	log.SetOutput(ioutil.Discard)
}

// 检查代理是否可用
func checkProxy(proxy Proxy, protocol, mode string, timeout time.Duration, wg *sync.WaitGroup, mu *sync.Mutex, goodProxies *[]Proxy, checkedIPs map[string]bool) {
	defer wg.Done()

	// 确保IP只检查一次
	mu.Lock()
	if checkedIPs[proxy.IP] {
		mu.Unlock()
		return
	}
	checkedIPs[proxy.IP] = true
	mu.Unlock()

	proxyURL := fmt.Sprintf("%s://%s:%s", protocol, proxy.IP, proxy.Port)
	proxyParsed, err := url.Parse(proxyURL)
	if err != nil {
		return
	}

	client := &http.Client{
		Transport: &customTransport{
			transport: &http.Transport{
				Proxy: http.ProxyURL(proxyParsed),
				TLSClientConfig: &tls.Config{
					InsecureSkipVerify: true,
				},
			},
		},
		Timeout: timeout,
	}

	var testURL string
	switch mode {
	case "icanhazip":
		testURL = "https://icanhazip.com" // 使用HTTPS测试URL
	case "azenv":
		testURL = "http://azenv.net"
	default:
		fmt.Printf("未知模式: %s\n", mode)
		return
	}

	startTime := time.Now()
	resp, err := client.Get(testURL)
	duration := time.Since(startTime)

	if err != nil {
		return
	}
	defer resp.Body.Close()

	// 确认响应体内容
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil || resp.StatusCode != 200 {
		return
	}

	// 根据测试URL的特性检查内容
	var validContent bool
	switch mode {
	case "icanhazip":
		validContent = strings.TrimSpace(string(body)) == proxy.IP
	case "azenv":
		validContent = strings.Contains(string(body), "REMOTE_ADDR")
	}

	if !validContent {
		return
	}

	green := "\033[32m"
	reset := "\033[0m"

	fmt.Printf(green+"成功: %s:%s [%s]\n"+reset, proxy.IP, proxy.Port, duration)
	mu.Lock()
	*goodProxies = append(*goodProxies, proxy)
	mu.Unlock()
}

// 从文件中读取代理列表
func readProxies(fileName string) ([]Proxy, error) {
	file, err := os.Open(fileName)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var proxies []Proxy
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := scanner.Text()
		parts := strings.Split(line, ":")
		if len(parts) == 2 {
			proxies = append(proxies, Proxy{IP: parts[0], Port: parts[1]})
		}
	}

	if err := scanner.Err(); err != nil {
		return nil, err
	}
	return proxies, nil
}

// 将可用的代理写入文件
func writeGoodProxies(fileName string, goodProxies []Proxy) error {
	file, err := os.Create(fileName)
	if err != nil {
		return err
	}
	defer file.Close()

	for _, proxy := range goodProxies {
		file.WriteString(fmt.Sprintf("%s:%s\n", proxy.IP, proxy.Port))
	}
	return nil
}

func main() {
	// 禁用默认日志输出
	disableLogging()

	// ANSI 转义序列，红色字体
	red := "\033[31m"
	reset := "\033[0m"

	// 解析命令行参数
	if len(os.Args) != 7 {
		fmt.Println(red + "如果你使用的是linux请先运行'ulimit -n 999999'，否则会影响质量!!!" + reset)
		fmt.Println(red + "本教程仅熟悉协议，请勿非法使用，后果自负，与我无关。" + reset)
		fmt.Println(red + "用法：./check [mode] [protocol] [input] [output] [timeout] [coroutine]" + reset)
		fmt.Println(red + "模式：icanhazip azenv" + reset)
		fmt.Println(red + "协议：http https" + reset)
		return
	}

	mode := os.Args[1]
	protocol := os.Args[2]
	inputFile := os.Args[3]
	outputFile := os.Args[4]
	timeout, err := strconv.Atoi(os.Args[5])
	if err != nil {
		fmt.Println("无效的超时时间。")
		return
	}
	coroutines, err := strconv.Atoi(os.Args[6])
	if err != nil {
		fmt.Println("无效的并发数量。")
		return
	}

	// 读取代理列表
	proxies, err := readProxies(inputFile)
	if err != nil {
		fmt.Println("读取代理文件错误:", err)
		return
	}

	startTime := time.Now()
	var wg sync.WaitGroup
	var mu sync.Mutex
	var goodProxies []Proxy
	checkedIPs := make(map[string]bool)

	// 使用信号量控制并发数量
	sem := make(chan struct{}, coroutines)
	for _, proxy := range proxies {
		wg.Add(1)
		sem <- struct{}{}
		go func(proxy Proxy) {
			defer func() { <-sem }()
			checkProxy(proxy, protocol, mode, time.Duration(timeout)*time.Second, &wg, &mu, &goodProxies, checkedIPs)
		}(proxy)
	}

	wg.Wait()

	// 写入可用代理到输出文件
	err = writeGoodProxies(outputFile, goodProxies)
	if err != nil {
		fmt.Println("写入可用代理文件错误:", err)
	}

	// 打印总结信息
	duration := time.Since(startTime)
	fmt.Printf(red+"已完成检查代理[%d]已保存到%s，存活代理为%d，检查模式为[%s]。[%s]\n"+reset, len(proxies), outputFile, len(goodProxies), mode, duration)
	fmt.Println(red + "感谢您使用。群聊TG：@heikeddos" + reset)
}
