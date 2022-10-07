const express = require('express')
const carbone = require('carbone')
const path = require('path')
const fs = require('fs')
const util = require('util')
const app = express()
const port = 3000
const userdataPath = "../userdata"
const outputFolderPath = "../build"
const templatePath = './reads_template.docx'
const renderOptions = {
    convertTo: 'pdf',
    reportName: 'read_{d.gid}_{d.id}.pdf'
}
const readFile = util.promisify(fs.readFile)
const writeFile = util.promisify(fs.writeFile)


app.get('/generate-report', async (req, res) => {
    const filename = req.query.filename
    console.log(filename)

    if (!filename) {
        res.statusCode = 400
        res.send("Filename is empty")
        return
    }

    let userdata
    try { 
        console.log("Going to read userdata")
        userdata = await getUserdata(filename)
    } catch(error) { 
        console.error(error)
        res.statusCode = 400
        res.send("Unable read userdata")
        return
    }

    carbone.render(templatePath, userdata, renderOptions, async (err, result, reportName) => {
        if(err) { 
            res.status = 400
            res.send("Render error")
        }

        const outputPath = path.join(outputFolderPath, reportName);

        try {
            await writeFile(outputPath, result)
            res.send("Done")
        } catch(error) { 
            console.error(error)
            res.status = 400
            res.send("Unable to write report to disk")
        }
    });
})

app.listen(port, () => {
    console.log(`Example app listening on port ${port}`)
})

async function getUserdata(filename) {
    const filePath = path.join(userdataPath, filename)
    const data = await readFile(filePath)
    return JSON.parse(data)
}