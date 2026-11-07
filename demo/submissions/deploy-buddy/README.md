# Deploy Buddy

A Switch agent that watches your deploy channel and rolls back bad releases
after a human types `!approve-rollback`.

Demo: https://www.loom.com/share/deploy-buddy-demo

## How Switch is used
The `deploy-buddy` agent joins your #deploys room through Switch and listens
for alerts.

## Run

```bash
npm install
npm test
```
