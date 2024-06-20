---
title: mybatis
date: 2021-08-20 18:07:21
tags: mybatis
categories: blog1
---

### mybatis进阶

1、首先实体类中需要在实体类中增加 list字段,在主类中增加

ps: 一个老师有多个学生，老师的类为A 学生的类为B ，那么在A中增加B的list

```
    private List<FinAuditDetal> finAuditDetalList;
```

association 与collection 的区别

association： 用于 *一对一关系的配置*

collection ：用于 一对多关系的配置

```
    <resultMap id="BathDetailResultMap" type="com.bijiangzb.loan.finance.infra.gateway.impl.db.model.FinAuditDO">
        <id column="BILL_ID" jdbcType="VARCHAR" property="billId"/>
        <collection property="finAuditDetalList"
                    ofType="com.bijiangzb.loan.finance.infra.gateway.impl.db.model.FinAuditDetalDO">
            <id column="FAD_AMOUNT" jdbcType="DECIMAL" property="fadAmount"/>
        </collection>
    </resultMap>
```

