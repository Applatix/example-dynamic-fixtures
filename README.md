# Dynamic Fixtures Example

This repository contains example code and service templates which utilizes Applatix's dynamic fixtures feature.

Dynamic fixtures can be used in `workflow` service templates and are defined by adding a `fixtures:` section in the service template. Dynamic fixtures reference other `container` service templates through the `template:` field. 

```
---
type: service_template
subtype: workflow
name: example-dynamic-fixtures
description: Clone the Applatix/example-dynamic-fixtures repo and run perf tests against database fixtures
fixtures:
  - mongodb:
      template: mongodb
    redisdb:
      template: redis
inputs:
  parameters:
    commit:
      default: "%%session.commit%%"
    repo:
      default: "%%session.repo%%"
    iterations:
      default: 100000
steps:
  - checkout:
      template: axscm-checkout
  - test:
      template: python-dbtest
      parameters:
        checkout: "%%steps.checkout%%"
        redis_ip: "%%fixtures.redisdb.ip%%"
        mongodb_ip: "%%fixtures.mongodb.ip%%"

```

During execution of the `example-dynamic-fixtures` workflow, two database container instances, MongoDB and Redis, will be launched for the duration of the workflow. The IP address of the containers can be referenced via the `%%fixtures.<fixture_name>.ip%%` attribute of the fixtures.

In this example, the Redis IP address and MongoDB IP are passed as input parameters to the `python-dbtest` service template, which the test can use to perform its tests.

```
---
type: service_template
subtype: container
name: python-dbtest
description: Run key/value insertion & retrieval tests against MongoDB and Redis
container:
  image: python:3.5.2
  resources:
    mem_mib: 256
    cpu_cores: 0.1
  command: sh -c "pip install -r /src/requirements.txt && /src/dbtest.py --redis %%redis_ip%% --mongodb %%mongodb_ip%% --iterations %%iterations%%"
inputs:
  parameters:
    checkout:
    redis_ip:
    mongodb_ip:
    iterations:
  artifacts:
  - from: "%%service.checkout.code%%"
    path: "/src"
```

Upon completion of the workflow, dynamic fixtures are automatically terminated.
