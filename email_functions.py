import smtplib, ssl, base64

from email import encoders
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

import pandas as pd
import pickle
import os

    
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
    monthly_summary_email = ""
    monthly_summary = []
    #Create an html-formatted string to inject into the email body for only the months included
    for month, count in zip(trx_per_month.index, trx_per_month):
        monthly_summary_email += f"<br>Number of transactions in {month}: {count}</br>\n"
        monthly_summary.append([month, count])
    return trxns, total_balance, avg_credit, avg_debit, monthly_summary, monthly_summary_email

def createTrxnsSummaryMessage(total_balance, avg_credit, avg_debit, monthly_summary_email):
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
    filename = "images/imageslogo_knot.png"
    image = base64.b64encode(open(filename, "rb").read())
    image_base64 = image.decode()

    
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
                                {monthly_summary_email}
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
                    <br><img align="left" width="150" height="150" src= "data:image/jpg;base64,{image_base64}"></br>
                </p>
            </div>
        </body>

    </html>
    """
    html_text = MIMEText(html, "html")
    message.attach(html_text)
    
    return message

def sendEmailTLS(credentials, receiver_email, subject, message, *filename):
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

        with open(filename[0], "rb") as attachment:
    
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read()) 
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename[0]}",
        )
        message.attach(part)
    
    try:
        smtp = smtplib.SMTP("smtp-mail.outlook.com", 587)
        smtp.starttls()
        smtp.login(sender_email, password)
        smtp.sendmail(sender_email, receiver_email, message. as_string())
        smtp.quit()
        
        return f"email sent successfully to {receiver_email}"
    except Exception as e:
        return f"error sending email: {e}"
