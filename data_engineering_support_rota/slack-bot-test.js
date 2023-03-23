import * as http from 'http';


// // the unique part of the hook; make this a github secret?
// const hook = 'T02DYEB3A/B04S06LHW3V/JHNvwWGShEoFFABQr9lZDMqA'

// var msg = 'Hello World';
// console.log(msg);


// const slackBody = {
//   mkdwn: true,
//   text: `Good Day!`
// };

// const res = request({
//   url: 'https://hooks.slack.com/services/${hook}',
//   method: 'POST',
//   body: slackBody,
//   json: true
// })

// console.log(res)

POST https://hooks.slack.com/services/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
Content-type: application/json
{
    "text": "Hello, world."
}