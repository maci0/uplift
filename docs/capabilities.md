# Uplift Maturity Model

The maturity model evaluates products across **5 categories** and **42 capabilities**. Each capability is scored on a scale of 1 (lowest) to 4 (highest). Some capabilities have minimum thresholds that define cloud readiness requirements.

---

## Category A: Code (12 capabilities)

### A1 -- Code Commenting Strategy

| Level | Description |
|-------|-------------|
| 1 | No or inconsistent code comments that do not follow any defined standards; comments cannot be used to generate documentation |
| 2 | All new code is self-documenting and comments are suitable for documentation generation tools |
| 3 | Most code is self-documenting and existing comments are suitable for documentation generation tools |
| 4 | All code is self-documenting and comments are consistently suitable for documentation generation tools |

### A2 -- Code Management Strategy
**Minimum threshold: 1**

| Level | Description |
|-------|-------------|
| 1 | Code is in SCM (e.g. git) and used for release, but there is little to no documented or agreed strategy of how to branch, merge, or release code |
| 2 | Develop on version branches. Every deployment can be tracked back to understand all changes which went into it by anyone in the team |
| 3 | Develop on feature branches that are short-lived (less than two weeks) and release from merged master |
| 4 | Develop and release from master with at least daily code check-ins using a process allowing traceability to the requested feature |

### A3 -- Test Suite
**Minimum threshold: 3**

| Level | Description |
|-------|-------------|
| 1 | No or some unit tests, functional tests, critical path tests, and performance tests |
| 2 | Some unit tests, functional tests, critical path tests, performance tests with all of them passing successfully |
| 3 | Actively builds and maintains unit tests, functional tests, critical path tests, performance tests with all of them successfully passing for positive flows |
| 4 | Actively builds and maintains unit tests, functional tests, critical path tests, performance tests with all of them successfully passing for positive and negative flows maintaining 100% critical path coverage |

### A4 -- Logging and Telemetry
**Minimum threshold: 2**

| Level | Description |
|-------|-------------|
| 1 | Default or customized logging and no telemetry |
| 2 | Rudimentary logging and telemetry in place |
| 3 | Adherence to established logging and telemetry standards. Suitable information available in logs and telemetry for troubleshooting common issues |
| 4 | Adherence to established logging and telemetry standards. Most issues can be diagnosed through logs and telemetry |

### A5 -- Backward / Forward Compatibility
**Minimum threshold: 2**

| Level | Description |
|-------|-------------|
| 1 | Breaking changes (i.e. tested locally) |
| 2 | Changes are regressed by users of the product prior to release |
| 3 | Coding practices support forward compatibility |
| 4 | Coding practices support backward and forward compatibility |

### A6 -- Monitoring and Alerting
**Minimum threshold: 2**

| Level | Description |
|-------|-------------|
| 1 | Logs have enough data to set up monitoring and alerts on |
| 2 | Some monitoring and some alerting is prioritized in the work queue |
| 3 | Prioritization of monitoring and alerting as part of the acceptance criteria for all work. Access to log archives and telemetry is available for troubleshooting |
| 4 | Prioritization of monitoring, alerting, and validation of triggers (e.g. SLAs) as part of the acceptance criteria for all work. Logs are indexed and telemetry is readily available for troubleshooting |

### A7 -- Quality Engineering Model

| Level | Description |
|-------|-------------|
| 1 | Contributors have separate roles (i.e. only code or test) |
| 2 | Some contributors can both code and test |
| 3 | Most contributors both code and test |
| 4 | All contributors both code and test |

### A8 -- Code Reuse

| Level | Description |
|-------|-------------|
| 1 | Contributors usually code what they need |
| 2 | Contributors can highlight where they have reused open source or code from other projects |
| 3 | Contributors aim to reuse vs rebuild while coding and actively evangelize to maximize code reuse by others |
| 4 | Contributors seek to reuse vs rebuild as part of the planning process, actively evangelize to maximize code reuse by others, and actively contribute to other code |

### A9 -- Build for Availability
**Minimum threshold: 2**

| Level | Description |
|-------|-------------|
| 1 | Product is not tested for extreme failures (e.g. a node/instance becoming unavailable) |
| 2 | Product is manually tested for extreme failures and automatically tested for error use cases |
| 3 | Automated resilience testing framework (e.g. Chaos Monkey) runs rampant on the product in a staging environment without failures |
| 4 | Automated resilience testing framework (e.g. Chaos Monkey) runs rampant on the product in staging and production without failures; all errors (code, web server, OS, etc.) are caught and escalated |

### A10 -- Incremental Coding (Prototyping)

| Level | Description |
|-------|-------------|
| 1 | Contributors do not use prototyping to estimate or validate any features |
| 2 | Contributors sometimes use prototyping to estimate larger features more confidently |
| 3 | Contributors often use prototyping to validate features with users before completion |
| 4 | Contributors always use prototyping to validate features with users before completion |

### A11 -- Feedback and Requirements

| Level | Description |
|-------|-------------|
| 1 | Contributors start coding before requirements are fully understood |
| 2 | Contributors code from wireframes / design comps and understand the requirements and business value before building the feature |
| 3 | Contributors code from wireframes / design comps, and understand how the feature interacts within the ecosystem before building the feature |
| 4 | Contributors code from clickable wireframes / design comps that were validated by users and understand how the feature interacts within the ecosystem before building the feature |

### A12 -- Behavior Driven Development (BDD)

| Level | Description |
|-------|-------------|
| 1 | Contributors do not have an understanding of BDD methodology |
| 2 | Contributors understand BDD methodology and practice it on some features |
| 3 | Contributors understand BDD methodology and practice it on most features |
| 4 | BDD methodology is how things get done |

---

## Category B: Build and Test (8 capabilities)

### B1 -- Definition of Done Completeness

| Level | Description |
|-------|-------------|
| 1 | Contributors do not follow any documented or agreed upon definition of "done" |
| 2 | Contributors mostly follow a defined definition of "done" |
| 3 | Contributors always follow definition of "done" as a gate to making a release |
| 4 | Contributors actively update definition of "done" to improve quality and prevent issues from reoccurring |

### B2 -- Code Quality

| Level | Description |
|-------|-------------|
| 1 | Code coverage is unknown or out of date |
| 2 | Code coverage is actively tracked |
| 3 | 80%+ code coverage is maintained |
| 4 | 90%+ code coverage is maintained or less than 20% of build rejections by regression test coverage |

### B3 -- Security Code Analysis
**Minimum threshold: 2**

| Level | Description |
|-------|-------------|
| 1 | Code has never been scanned with a web application security scanner |
| 2 | Code has been previously scanned with a security scanner |
| 3 | Code is regularly scanned with a security scanner |
| 4 | Code is automatically scanned with a security scanner and defects are prioritized into active workload |

### B4 -- Automated Testing
**Minimum threshold: 2**

| Level | Description |
|-------|-------------|
| 1 | No defined acceptance tests |
| 2 | Some existing acceptance tests, but little to no automation |
| 3 | Most existing tests are automated, but all new acceptance tests are fully automated |
| 4 | Acceptance tests are actively built and maintained with full automation for every build |

### B5 -- Continuous Integration
**Minimum threshold: 3**

| Level | Description |
|-------|-------------|
| 1 | No automated build pipeline. Code is manually compiled and may not always compile successfully |
| 2 | Build pipeline contains manual steps but the build is never left in a failed state. Some failures may be missed |
| 3 | Build pipeline requires automated tests to pass before feature is considered "complete" |
| 4 | Build pipeline requires automated tests to pass and failures are actively monitored; a process for handling failures is in place |

### B6 -- Performance Testing and Capacity Planning
**Minimum threshold: 2**

| Level | Description |
|-------|-------------|
| 1 | The operational capacity of the production software is not clearly understood |
| 2 | Performance is manually tested during the release process using load scripts of common scenarios. Contributors understand the algorithmic complexity of the software |
| 3 | Performance is automatically tracked in a staging environment to gauge changes in application performance. Contributors understand the optimal load that each instance can handle, and there is a process in place to make release decisions based on acceptance of new SLAs. Capacity provisioning and scaling requires manual steps |
| 4 | Performance is automatically tracked in both staging and production with a full understanding of the application performance characteristics. Contributors actively collaborate with the business to determine acceptance of new SLAs based on actual production traffic and predictions created by load testing. Capacity provisioning and scaling is fully automated |

### B7 -- Configuration File Management
**Minimum threshold: 3**

| Level | Description |
|-------|-------------|
| 1 | Manual configurations |
| 2 | Each environment has predefined configurations |
| 3 | Sensitive data has been abstracted, and configurations are human readable |
| 4 | Sensitive data has been abstracted, and configurations are human readable. All configurations are automated with tools that support monitoring and alerting with minimal environment-specific data |

### B8 -- Service Consumer Tests
**Minimum threshold: 2**

| Level | Description |
|-------|-------------|
| 1 | No or some tests simulating a consuming application or service |
| 2 | Manual tests are executed to simulate a consuming application or service |
| 3 | Automated tests of main use cases from a consuming application or service are integrated into the build pipeline |
| 4 | Automated tests from a consuming application or service are triggered by the build pipeline and cause the build to fail if there are errors |

---

## Category C: Release (10 capabilities)

### C1 -- Deployment Strategy
**Minimum threshold: 2**

| Level | Description |
|-------|-------------|
| 1 | Contributors do not follow a documented or consistent deployment strategy |
| 2 | Contributors follow a defined deployment strategy |
| 3 | Contributors follow a defined deployment strategy that includes automated rollbacks, regression tests, configs, and tracking |
| 4 | Contributors follow a defined deployment strategy that is fully automated and includes regression tests, configs, tracking, and database releases |

### C2 -- Release Frequency

| Level | Description |
|-------|-------------|
| 1 | Releases take longer than a cycle (iteration / sprint) |
| 2 | 1 release every cycle (sprint / iteration) |
| 3 | Multiple releases every cycle (sprint / iteration) |
| 4 | Code is released to production on every successful build |

### C3 -- Feature Flags

| Level | Description |
|-------|-------------|
| 1 | No feature flagging |
| 2 | Some feature flagging |
| 3 | Feature flags adhere to an established standard, allow for run-time based configuration, and are consistently maintained as the product evolves |
| 4 | Feature flags adhere to an established standard, allow for run-time based configuration, are consistently maintained as the product evolves, and different categories of feature flags are controlled by different stakeholders |

### C4 -- Build Pipeline Traceability
**Minimum threshold: 1**

| Level | Description |
|-------|-------------|
| 1 | Code can be built correctly -- manually or via a build pipeline |
| 2 | There is a build pipeline with a visual representation and contributors are automatically alerted when a build fails |
| 3 | Build is triggered by source control check-in or is scheduled, with alerts being sent out on failures |
| 4 | Build is triggered by source control check-in or a build of its dependent services, with alerts being sent out on failures, and if successful the build is pushed across environments to production |

### C5 -- Modular Releases

| Level | Description |
|-------|-------------|
| 1 | Entire product is a single deployable unit |
| 2 | Some of the product is separated into different deployable units |
| 3 | Most of the product is separated into many deployable units |
| 4 | Pieces of product/service are independently deployable and the lifecycle of change for different parts of the product is well understood and taken into account for the deployment architecture |

### C6 -- Continuous Delivery
**Minimum threshold: 2**

| Level | Description |
|-------|-------------|
| 1 | Manual deployment and testing are performed in staging |
| 2 | Manual deployment and automatic testing are performed in staging |
| 3 | Automated deployment and tests are performed in staging |
| 4 | Automated deployment and tests are performed in production when code is checked in as "zero touch" continuous deployments |

### C7 -- Deployment Methodology

| Level | Description |
|-------|-------------|
| 1 | Able to automatically or manually deploy a new release to a single server/cluster before rolling to the next |
| 2 | Able to manually determine the impact of a partial (canary) deployment |
| 3 | Able to automatically determine the impact of a partial (canary) deployment |
| 4 | Zero downtime, fully automated blue-green or red-black deployments spin up and validate a canary instance in production with the ability to segment a group or percentage of traffic, switch traffic over, and shut down the previous version once successful |

### C8 -- Dependency Management

| Level | Description |
|-------|-------------|
| 1 | Dependencies are uncertain |
| 2 | Manual dependency management |
| 3 | Automatic dependency management |
| 4 | Contributors follow a defined strategy to regularly update dependencies to newer versions |

### C9 -- Push Button Releases

| Level | Description |
|-------|-------------|
| 1 | Releases require more than one contributor to deploy |
| 2 | Releases require manual intervention |
| 3 | Code can be deployed via a push button release, but not the environment |
| 4 | Production-like environments can be prepared through version controlled scripts and run via push button deployments |

### C10 -- Scriptable DB Releases

| Level | Description |
|-------|-------------|
| 1 | Database specialist makes schema / migrations on behalf of the contributors |
| 2 | Contributors create scripts to perform schema changes and migrations, but database specialist executes them |
| 3 | DB schema changes and migrations are made directly from version control as a manual step during release |
| 4 | DB schema changes and migrations are made directly from version control and consistent across all environments, including production |

---

## Category D: Operate (8 capabilities)

### D1 -- DevOps Practice

| Level | Description |
|-------|-------------|
| 1 | Environments in production are not controlled by contributors building the product |
| 2 | Environments in staging are controlled and partially managed by the contributors building the product and receive issue escalations for that environment |
| 3 | Environments in production are owned by the contributors building the product, but controlled by someone else |
| 4 | DevOps model is followed -- environments in production are fully controlled and owned by the contributors building the product, including alerts and issue escalations |

### D2 -- Runbook Adoption

| Level | Description |
|-------|-------------|
| 1 | No triage runbook has been created |
| 2 | Contributors have created a triage runbook, but it is not actively used |
| 3 | Contributors have created a triage runbook, and it is integrated into the alerting infrastructure for easy reference |
| 4 | Contributors have created a useful triage runbook that is actively maintained and integrated into the alerting infrastructure for easy reference |

### D3 -- Monitoring and Alerting
**Minimum threshold: 2**

| Level | Description |
|-------|-------------|
| 1 | SLAs haven't been defined or, if monitored, alerts mostly just encompass the standard cases |
| 2 | SLAs are monitored and some alerts are sent when thresholds are not met. Healthchecks are monitored and alerts are configured for many standard error conditions |
| 3 | SLAs in staging and production are consistently being met and alerted on when thresholds are not met. Healthchecks are monitored. Alerts are configured for a majority of error conditions |
| 4 | SLAs in staging and production are consistently being met, and a business disruption alert is escalated when thresholds are not met or a healthcheck fails. Non-standard HTTP responses trigger an alert. Alerts are triggered for main use cases when expected results are not met (e.g. lower than normal conversion rate) |

### D4 -- On-Call Strategy
**Minimum threshold: 2**

| Level | Description |
|-------|-------------|
| 1 | Others know how to escalate to the team |
| 2 | Contributors follow a defined on-call strategy |
| 3 | On-call strategy is efficient as evidenced by consistently low MTTD and MTTR but sometimes requires more than one party to resolve |
| 4 | Contributor who is on-call is usually the resolver for all issues within their product as evidenced by a consistently low MTTD and MTTR |

### D5 -- Risk Management
**Minimum threshold: 2**

| Level | Description |
|-------|-------------|
| 1 | Contributors do not fully own risk management or mitigation of the product. Disaster recovery is normally defined and/or managed by someone else who has full ownership |
| 2 | Contributors think about disaster recovery plans while the code is built and released, but requires the involvement from many other parties |
| 3 | There is an established disaster recovery plan (DRP) and business continuity program (BCP) |
| 4 | There is an established DRP and BCP which has been tested within the past 6 months |

### D6 -- Synthetic Monitoring
**Minimum threshold: 2**

| Level | Description |
|-------|-------------|
| 1 | No synthetic monitoring is in place |
| 2 | Synthetic monitoring is used in staging and production with some alerting |
| 3 | Synthetic monitoring is used in staging and production for major use cases, with escalation alerts for failures |
| 4 | Synthetic monitoring is used in staging and production for both positive and negative use cases, with escalation alerts for failures |

### D7 -- Log Management Strategy
**Minimum threshold: 2**

| Level | Description |
|-------|-------------|
| 1 | All logs, all the time! |
| 2 | Log rotation is based off a default template |
| 3 | Log rotation takes into account available disk space. Logs are archived for retention |
| 4 | There is an effectively defined log rotation strategy including timing of business activities like periods of high demand. Logs are retained according to business and legal requirements |

### D8 -- Business Dashboard

| Level | Description |
|-------|-------------|
| 1 | Some business metrics are tracked in a dashboard and/or some metrics are still mined manually, but these may not be visible or accessible to all contributors |
| 2 | Business metrics are tracked in a dashboard that illustrates product performance and is constantly referenced by others to quantify how the product performs. All contributors have access and regular consistent visibility of the dashboard |
| 3 | Business metrics are tracked in a dashboard that illustrates product performance, is constantly referenced by others, and used to measure the success of new feature rollouts. The dashboard is clearly visible at all times to all contributors |
| 4 | Business metrics are tracked in a dashboard that illustrates product performance, is constantly referenced by others, and used to measure the success of new feature rollouts. Main use cases trigger alerts to stakeholders when business metrics do not match expected values (e.g. lower than expected conversion rates) |

---

## Category E: Optimize (4 capabilities)

### E1 -- Continuous Process Improvement

| Level | Description |
|-------|-------------|
| 1 | Few processes are defined and contributors rely on tribal knowledge to succeed |
| 2 | Processes are documented and can be repeated by any contributor |
| 3 | Contributors simplify / automate processes whenever possible and documentation is maintained as they evolve |
| 4 | Contributors are actively focused on continuous process improvement by identifying and enhancing processes; performance is predictable and quality is consistently high |

### E2 -- Tech Debt Management

| Level | Description |
|-------|-------------|
| 1 | Contributors do not track debt in any consistent way |
| 2 | Contributors can track debt via a defined process |
| 3 | Contributors avoid taking on any new debt by actively tracking and managing it |
| 4 | Contributors actively prioritize and reduce all debt |

### E3 -- Root Cause Prevention
**Minimum threshold: 2**

| Level | Description |
|-------|-------------|
| 1 | Production issues happen and sometimes it is known why, but it is mostly difficult to find the underlying cause |
| 2 | Contributors follow a defined process for determining the root cause of issues |
| 3 | Contributors follow a defined and accepted process for determining the root cause of issues, and major issues are prioritized and corrected |
| 4 | Contributors follow a defined and accepted process for root cause analysis which includes consistently preventing future issues by: 1) putting the issue into the work queue, 2) prioritizing and correcting the issue, and 3) adding monitoring or alerting to detect such issues |

### E4 -- Data-Driven Metrics

| Level | Description |
|-------|-------------|
| 1 | It takes a lot of time to gather metrics and sometimes it is too late to get the data after the fact |
| 2 | Metrics can be pulled after an issue happens to determine why |
| 3 | Metrics illustrate the product health, and action (e.g. product decisions) is taken based on the metrics |
| 4 | Metrics illustrate the product health, predictive rules create alerts, and action (e.g. product decisions) is taken based on the metrics |

---

## Scoring

Each capability is scored 1-4. Category scores are the average of their capability scores. The overall score is the percentage of capabilities that meet or exceed their minimum threshold (capabilities without a minimum threshold are excluded from this calculation).

### Capabilities with minimum thresholds

| Capability | Minimum |
|------------|---------|
| A2 -- Code Management Strategy | 1 |
| A3 -- Test Suite | 3 |
| A4 -- Logging and Telemetry | 2 |
| A5 -- Backward / Forward Compatibility | 2 |
| A6 -- Monitoring and Alerting | 2 |
| A9 -- Build for Availability | 2 |
| B3 -- Security Code Analysis | 2 |
| B4 -- Automated Testing | 2 |
| B5 -- Continuous Integration | 3 |
| B6 -- Performance Testing and Capacity Planning | 2 |
| B7 -- Configuration File Management | 3 |
| B8 -- Service Consumer Tests | 2 |
| C1 -- Deployment Strategy | 2 |
| C4 -- Build Pipeline Traceability | 1 |
| C6 -- Continuous Delivery | 2 |
| D3 -- Monitoring and Alerting | 2 |
| D4 -- On-Call Strategy | 2 |
| D5 -- Risk Management | 2 |
| D6 -- Synthetic Monitoring | 2 |
| D7 -- Log Management Strategy | 2 |
| E3 -- Root Cause Prevention | 2 |

21 of the 42 capabilities have minimum thresholds. The overall "cloud score" percentage reflects how many of these 21 thresholds are being met.
