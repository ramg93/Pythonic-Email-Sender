import smtplib, ssl

from email import encoders
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

import pandas as pd
import pickle
import os

def credentials():
    if not os.path.exists('secret_credentials.pkl'):
        credentials={}
        credentials['Sender Email'] = "" # sender email account
        credentials['Sender Password'] = "" # sender email account password
        credentials['Receiver Email'] = "" # receiver email account
        with open('secret_credentials.pkl','wb') as f:
            pickle.dump(credentials, f)
    else:
        credentials=pickle.load(open('secret_credentials.pkl','rb'))
        
    return credentials
    
def df2Summary(trxns):
    '''
        input =>    
            trxns_file: Pandas Data Frame
        output =>   
            trxns: Pandas DataFrame
            total_balance: Float
            avg_credit: Float
            avg_debit: Float
            monthly_sumarry: String
                
    '''
    #Total Balance
    total_balance = trxns.transaction.sum() # sum of transactions
    #Debit and Credit Averages
    trxns["DebitorCredit"] = trxns.transaction.map( lambda x: 'credit' if x > 0 else 'debit')
    avg_credit = trxns.loc[trxns.DebitorCredit == "credit", 'transaction'].mean()
    avg_debit = trxns.loc[trxns.DebitorCredit == "debit", 'transaction'].mean()
    #Monthly Summaries
    trxns['c'] = pd.to_datetime(trxns.created_at, format = "%Y-%m-%d")
    trxns['month'] = trxns.c.dt.strftime("%B")
    trx_per_month = trxns.month.value_counts()
    #monthly_summary = ""
    monthly_summary = []
    #Create an html-formatted string to inject into the email body for only the months included
    for month, count in zip(trx_per_month.index, trx_per_month):
        #monthly_summary += f"<br>Number of transactions in {month}: {count}</br>\n"
        monthly_summary.append([month, count])
    return trxns, total_balance, avg_credit, avg_debit, monthly_summary

def createTrxnsSummaryMessage(total_balance, avg_credit, avg_debit, monthly_summary):
    '''
        Input =>
            total_balance: Float
            avg_credit: Float
            avg_debit: Float
            monthly_summary: String
        Output=>
            message => SMTP.MIMEMultipart Message Object
    '''
    
    message = MIMEMultipart("alternative")

    
    html = f"""
    <html>
        <body>
            <div>
                <p>
                    Hello,<br>Herein is your Transactions Summary<br>
                </p>
            </div>
            <div>
                <table style="width:100%">
                      <tr>
                        <th>
                            <p>
                                <br>Total Balance: {total_balance}</br>
                                <br>Average Debit Amount: {avg_debit}</br>
                                <br>Average Credit Amount: {avg_credit}</br>
                            </p>
                        </th>
                        <th>
                            <p>
                                {monthly_summary}
                            </p>
                        </th>
                      </tr>
                </table>
            </div>  
            <div>
                <p>
                    <br>Engr. Raúl Armando Murga Garrido</br>
                    <br>B. Sc. Mechatronics Engineering</br>
                    <br><a href="https://www.linkedin.com/in/ra%C3%BAl-murga/">LinkedIn</a></br>
                    <br><a href="https://github.com/ramg93">GitHub</a></br>
                    <br><img align="left" width="150" height="150" src="cid:image1"></br>
                </p>
            </div>
        </body>

    </html>
    """
    html_text = MIMEText(html, "html")
    message.attach(html_text)

    fp = open('images/imageslogo_knot.png', 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()

    msgImage.add_header('Content-ID', '<image1>')
    message.attach(msgImage)
    
    return message

def sendEmailSLL(credentials, receiver_email, subject, message, *filename):
    '''
        Input =>
            credentials: Dict
            receiver_email: String
            subject: String
            message: String}
        Output =>
            None: print either success or exception
    '''
    
    sender_email = credentials['Sender Email']
    password =credentials['Sender Password']
    
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email
    
    if filename:

        with open(filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read()) 
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        message.attach(part)
    
    try:
        port = 465 # Assign 465 port for the SMTP server (Gmail's requirements)
        context = ssl.create_default_context() 

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, 
                receiver_email, 
                message.as_string()
            )
        print("email sent successfully")
    except Exception as e:
        print("error sending email: ", e)
