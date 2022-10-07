/** 1 . dependencies */
const carbone = require('carbone');
const fs = require('fs');

/** 2 . input template file name and output file name */
const _fileInputName = './reads_template.docx';

/** 3 . Data to inject */
const _data = require("./reads_data_sample.json")

/** 4 . Options object */
const _options = {
  convertTo: 'pdf',
  reportName: 'read_{d.id}.pdf'
};

/** 5 . Call carbone render function */
carbone.render(_fileInputName, _data, _options, (err, result, reportName) => {
  if (err) {
    console.log(err);
  } else {
    fs.writeFileSync('./build/' + reportName, result);
  }
  process.exit();
});