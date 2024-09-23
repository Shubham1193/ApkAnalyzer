const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const port = 3000;

app.use(bodyParser.urlencoded({ extended: false }));
app.use(express.json())

app.post('/sms', (req, res) => {
  const smsText = req.body.SMSText;

  // Process the SMS text here
  console.log('Received SMS:', smsText);

  // Example response
  res.json({ message: 'SMS received successfully' });
});

app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});