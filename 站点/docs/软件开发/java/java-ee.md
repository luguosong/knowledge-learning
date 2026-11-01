# Java EE 与 Tomcat


**结论**：Java 企业版（Java Platform, Enterprise Edition，Java EE，现 Jakarta EE）是一组规范，不是软件；Tomcat 是实现其中 Web 层子集（Servlet、JSP、EL、WebSocket）的开源 Servlet 容器。完整实现全部规范的软件叫应用服务器（如 GlassFish、WildFly、WebLogic）。Tomcat 听得多而 Java EE 听得少，因为：Tomcat 是可安装运行的具体产品、是 Web 子集的事实标准且被 Spring Boot 默认内嵌；「Java EE」之名已停用，完整平台话题又被 Spring 分流。

名称与归属演变：

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"LXGW WenKai, sans-serif","fontSize":"16px","textColor":"#1b1f24","lineColor":"#64748b","primaryColor":"#e7f5ff","primaryTextColor":"#0f4d7a","primaryBorderColor":"#1971c2","clusterBkg":"#f8f9fa","clusterBorder":"#cbd5e1","titleColor":"#1b1f24","edgeLabelBackground":"#ffffff"},"flowchart":{"useMaxWidth":false,"htmlLabels":false,"curve":"linear","nodeSpacing":24,"rankSpacing":36},"sequence":{"useMaxWidth":false,"wrap":true,"width":180,"actorMargin":50}}}%%
flowchart TB
    accTitle: Java EE 与 Tomcat
    j2ee["1999：Sun 发布 J2EE 1.2"]
    j2ee --> javaee["2006：Java EE 5 起，J2EE 更名 Java EE"]
    javaee --> eclipse["2017：Oracle 将 Java EE 移交 Eclipse 基金会，EE4J 项目"]
    eclipse --> jakarta["2019：更名 Jakarta EE，首版 Jakarta EE 8 与 Java EE 8 规范一致"]
    jakarta --> namespace["2020：Jakarta EE 9 起，命名空间 javax 改为 jakarta"]
    namespace --> tomcat["2026：Tomcat 11 对应 Jakarta EE 11 的 Web 层规范"]:::result
    classDef default fill:#e7f5ff,stroke:#1971c2,color:#0f4d7a,stroke-width:1.5px
    classDef result fill:#c5f6fa,stroke:#0c8599,color:#0a5a68,stroke-width:1.5px
```

Tomcat 与规范版本对应：Tomcat 9 对应 Java EE 8（Servlet 4.0，最后一个支持 `javax` 命名空间的大版本）；Tomcat 10.1 对应 Jakarta EE 10（Servlet 6.0）；Tomcat 11 对应 Jakarta EE 11（Servlet 6.1）。学习方向应按实际工程需求选择。

信源：

- [Apache Tomcat 版本与规范对应（一手）](https://tomcat.apache.org/whichversion.html)
- [Jakarta EE 官网（一手）](https://jakarta.ee/)
- [Jakarta EE About（一手）](https://jakarta.ee/about/)
- [Eclipse Foundation 博客：Java EE Moves to the Eclipse Foundation（一手，2017-09-12）](https://eclipse-foundation.blog/2017/09/12/java-ee-moves-to-the-eclipse-foundation)

### 证据与时效 · q-20261014-001

- **信源**：[一手] [Apache Tomcat 版本与规范对应](https://tomcat.apache.org/whichversion.html)；[Jakarta EE 官网](https://jakarta.ee/)；[Jakarta EE About](https://jakarta.ee/about/)；[Eclipse Foundation 博客：Java EE Moves to the Eclipse Foundation（2017-09-12）](https://eclipse-foundation.blog/2017/09/12/java-ee-moves-to-the-eclipse-foundation)。核实日期：2026-10-14。


## 提问记录

### q-20261014-001

- **原题**：2026-10-14 · Java EE 与 Tomcat 的关系及名称演变
- **问**：Java EE 和 Tomcat 之间是什么关系？为什么 Tomcat 听得多而很少听到 Java EE？
- **领域**：Java
- **首次**：2026-10-14
- **更新**：2026-10-14
- **正文**：[Java EE 与 Tomcat](#java-ee-与-tomcat)
- **关联**：[2026-09-22 · 成为 Java 专家的完整学习路线](index.md#q-20260922-001)
