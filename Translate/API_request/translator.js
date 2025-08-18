const express = require("express");
const app = express();

app.use(express.json());

//import routers

const deeplRouter = require("./Routes/deepl");
const caiyunRouter = require("./Routes/caiyun");
const tencentRouter = require("./Routes/tencent");
const xiaoniuRouter = require("./Routes/xiaoniu");
const baiduRouter=require("./Routes/baidu_api");
const bingRouter=require("./Routes/bing");
const googleApiRouter=require("./Routes/google_api");
const youdaoRouter=require("./Routes/youdao");



// mount routers
app.use("/translate/deepl", deeplRouter);
app.use("/translate/caiyun", caiyunRouter);
app.use("/translate/tencent", tencentRouter);
app.use("/translate/xiaoniu", xiaoniuRouter);
app.use("/translate/google", googleApiRouter);
app.use("/translate/youdao", youdaoRouter);
app.use("/translate/baidu", baiduRouter);
app.use("/translate/bing", bingRouter);



// start server
const PORT = 3000;
app.listen(PORT, () =>
  console.log(`✅ Translator API running at http://localhost:${PORT}`)
);
