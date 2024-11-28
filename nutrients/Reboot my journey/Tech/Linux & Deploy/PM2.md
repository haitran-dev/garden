Process manager keep application online on production

| Command              | Use                                                           | Example                                                 | Output                               |
| -------------------- | ------------------------------------------------------------- | ------------------------------------------------------- | ------------------------------------ |
| pm2 ls               | list current processes                                        |                                                         | ![[Pasted image 20241128142150.png]] |
| pm2 startup          | generate startup scripts to keep process list intact (stable) |                                                         | ![[Pasted image 20241128142351.png]] |
| pm2 start ==params== | start pm2 process                                             | pm2 start npm --name "portfolio-preview" -- run preview | ![[Pasted image 20241128144629.png]] |
| pm2 save             | to save current process list in pm2 config                    |                                                         |                                      |

With javascript project, can create system.config.cjs file for store pm2 parameters like this
```

```