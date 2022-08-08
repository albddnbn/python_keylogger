<h1>Experimental Python Keylogger</h1>
Experimental keylogger written in Python. Keylogger saves files to a './logfiles' directory.

<h3>Files created by keylogger:</h3>
<ul>
    <li>.log files containing record of keystrokes (one .log file created at end of each 'report interval'. Interval can be set to a semi-random value, like 10-15 seconds, for example.</li>
    <li>.png files - screenshots of all connected monitors/displays</li>
    <li>clipboard data can be saved to a .txt file</li>
    <li>Target system information saved to a .txt file</li>
    <li>output.zip folder also created which contains all above files</li>
</ul>

<p>Currently, keylogger can be configured to just create the files and the output.zip folder, or can be configured to send files and/or output.zip to specified SMTP server</p>

<h2>To set up local SMTP server:</h2>
<p>Use <a href="https://github.com/Nilhcem/FakeSMTP">https://github.com/Nilhcem/FakeSMTP</a> or something similar</p>

<p>The keylogger was set up to send emails to a specified Gmail address, but in May 2022 Google got rid of the option to allow access from "less secure apps", which is why a local SMTP server was used for the time being.</p>



