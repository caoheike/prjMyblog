IDEA快捷键

1、快速复制文件路径

```
CTRL+SHIFT+C
```

2、快捷生成序列化

1. **1.点击idea左上角File -> Settings -> Editor -> Inspections -> 搜索 Serialization issues ，找到 Serializable class without ‘serialVersionUID’ ->打上勾，再点击Apply->**

2. **2.OK返回你的代码，实体中只要实现了Serializable的类名都会暗黄，这个时候你只需要鼠标点击类名，alt+enter 就可以一键生成serialVersionUID**

   ###### 