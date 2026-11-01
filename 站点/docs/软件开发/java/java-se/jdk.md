# JDK：版本演化与类库体系

JDK 从 8 到 25 的三层换代，与公开类库体系的宏观地图。

## JDK 8 与 JDK 25 差别有多大

跨 11 年、17 个版本，三层换代：语言写法（`var`、`record`、密封类、模式匹配、文本块、模块导入、实例 `main`）、平台结构与默认行为（模块系统与强封装、移出 EE／CORBA／Nashorn／CMS、UTF-8 默认字符集、标准 HttpClient）、运行时（G1 起步到新一代 GC、虚拟线程、Scoped Values、紧凑对象头与 AOT）。向后兼容成立：8 的代码大多可在 25 编译运行；主体知识结构不变，但 8 基线资料需按 25 翻译语法与默认行为。

```text
2014 JDK 8     Lambda + Stream、默认方法、java.time
2017 JDK 9     模块系统 JPMS、jshell、G1 成为默认 GC
2018 JDK 10-11 var、标准 HttpClient、单文件直接运行、移出 Java EE 与 CORBA
2020 JDK 14-15 switch 表达式、文本块、移除 CMS 与 Nashorn
2021 JDK 16-17 record 与 instanceof 模式、密封类、内部 API 默认强封装
2022 JDK 18    UTF-8 成为默认字符集
2023 JDK 21    虚拟线程、switch 模式与记录模式
2025 JDK 25    Scoped Values、模块导入与实例 main、紧凑对象头与 AOT
```

| 层 | JDK 8（2014） | JDK 25（2025） |
| --- | --- | --- |
| 语言 | Lambda／Stream 刚引入（Project Lambda 是 8 的核心特性） | `var`（10）、switch 表达式（14）、文本块（15）、`record`（16）、`instanceof` 模式（16）、密封类（17）、switch／记录模式（21）、模块导入与实例 `main`（25） |
| 平台与 API | 类路径世界；EE 模块（JAXB 等）内置；平台默认字符集；HttpURLConnection | 模块系统（9，JEP 261）与内部 API 默认强封装（16／17，JEP 396／403）；EE／CORBA 移出（11，JEP 320）；UTF-8 默认字符集（18，JEP 400）；标准 HttpClient（11，JEP 321）；SecurityManager 弃用（17，JEP 411） |
| 运行时 | Parallel GC 默认；永久代刚改为元空间 | G1 默认（9 起，JEP 248）；CMS 移除（14，JEP 363）、Nashorn 移除（15，JEP 372）；虚拟线程（21，JEP 444）；Scoped Values（25，JEP 506）；紧凑对象头（25，JEP 519）与 AOT 缓存（25，JEP 514／515） |
| 工具链 | javac／java／jar | 加 jshell（9，JEP 222）、单文件源码直接运行（11，JEP 330）、jlink（9）与 jpackage（16） |

**8 基线资料的翻译清单**：

1. 语法糖重写：示例用 `var`、`record`、switch 表达式、文本块、instanceof／switch 模式改写，行为不变、表达更短。
2. 默认行为：字符集——8 按平台默认（中文 Windows 即 GBK，读文件经典乱码源），18 起默认 UTF-8；反射访问 JDK 内部 API——17 起默认拒绝。
3. 已移出／移除：JAXB／JAX-WS（11 起独立库）、CORBA（11）、Nashorn（15）、CMS GC（14）——8 资料相关章节作废；SecurityManager（17 起弃用）不再新学。
4. 网络示例：HttpURLConnection 换 HttpClient（11）。
5. 并发补充：Thread-per-request 思路在 21 起可用虚拟线程；ThreadLocal 部分场景可换 Scoped Values（25）。

信源（均一手，核实日期 2026-10-15）：[JDK 8 项目页](https://openjdk.org/projects/jdk8/)、[Java 语言特性演进表](https://docs.oracle.com/en/java/javase/21/language/java-language-changes-summary.html)、[JEP 索引](https://openjdk.org/jeps/0)、[JDK 25 项目页](https://openjdk.org/projects/jdk/25/)。

## JDK 类库体系的宏观概览

以 JDK 25 为基线，公开类库分为两类：Java SE 标准 API（模块名以 `java` 开头）和 JDK 专属 API（模块名以 `jdk` 开头）；前者以 `java.base` 为基础，再由其他模块提供数据库、文档、桌面、管理等能力。理解时先按职责定位，再按"模块 → 包 → 类／接口"查找。下列职责分组是教学归纳，不是官方固定分层。

```text
JDK 公开类库
+-- Java SE 标准 API（java.* 模块）
|   +-- java.base（其余命名模块都依赖它）
|   |     语言与对象（java.lang）、集合与函数式（java.util.*）、
|   |     数值/文本/时间、并发、I/O 与基础网络、安全与密码、
|   |     反射、方法句柄、外部函数与内存、class 文件处理
|   +-- java.net.http            > HttpClient 客户端
|   +-- java.sql / java.sql.rowset > 数据库访问
|   +-- java.naming / java.rmi / java.prefs
|   +-- java.xml / java.xml.crypto
|   +-- java.desktop / java.datatransfer > 桌面与多媒体
|   +-- java.logging / java.management(+rmi) / java.instrument
|   +-- java.compiler / java.scripting
+-- JDK 专属公开 API（jdk.* 模块）
    +-- jdk.compiler / jdk.jshell > 开发工具集成
    +-- jdk.jfr                   > 运行事件录制与消费
    +-- jdk.attach                > 附加目标虚拟机
    +-- jdk.httpserver            > 面向简单用途的服务端 API
```

**模块与包的分工**。示例：`java.base` → `java.util` → `List`／`ArrayList`；`java.logging` → `java.util.logging` → `Logger`。模块声明依赖与对外导出；包提供类型命名和组织。除 `java.base` 自身外，命名模块依赖 `java.base`。

**边界**：`javax.crypto`、`javax.sql`、`javax.swing` 均属于 Java SE，`javax` 不等于第三方或废弃；`jdk.jfr` 是公开 API，`jdk` 不等于内部实现；工具模块可以包含命令行工具实现，命令本身与可调用 API 应分开理解；JDBC 提供标准访问 API 与驱动框架，连接具体数据库通常另加对应驱动。桌面与多媒体模块 `java.desktop` 的技术版图见 [Java 图形化编程](图形化.md)。

信源（均一手，核实日期 2026-10-15）：[Java SE 25 与 JDK 25 API 总览](https://docs.oracle.com/en/java/javase/25/docs/api/index.html)、[java.base 模块](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/module-summary.html)、[模块描述与依赖](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/module/ModuleDescriptor.html)、[java.net.http](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/module-summary.html)、[java.sql 包与驱动框架](https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/package-summary.html)、[java.desktop](https://docs.oracle.com/en/java/javase/25/docs/api/java.desktop/module-summary.html)、[java.compiler](https://docs.oracle.com/en/java/javase/25/docs/api/java.compiler/module-summary.html)、[java.logging](https://docs.oracle.com/en/java/javase/25/docs/api/java.logging/module-summary.html)、[jdk.jfr](https://docs.oracle.com/en/java/javase/25/docs/api/jdk.jfr/module-summary.html)、[jdk.httpserver](https://docs.oracle.com/en/java/javase/25/docs/api/jdk.httpserver/module-summary.html)。

