#!/usr/bin/env python
import imaplib
import secrets
import pixhooks
import pdb

def fetch_update_emails(host, address, password):
    res = initiate_session(host, address, password)
    session = res['session']
    has_passphrase = False
    new_files = []
    for mid in res['inbox']:
        if not mid: # No messages
            continue
        subject, parts = fetch_subject_mime_parts(session, mid)
        images = []
        part_types = []
        for part in parts:
            part_type = ''
            for line in part:
                if "Content-Type" in line:
                    part_type = line.split(":")[1].strip().replace(";","")

                if secrets.passphrase.lower() in line.lower():
                    has_passphrase = True
            part_types.append(part_type)
        if has_passphrase:
            pixhooks.process_update_email(subject, zip(parts, part_types))
            session.store(mid, '+FLAGS', r'(\Deleted)')
        else:
            session.store(mid, '-FLAGS', r'(\Seen)')

    return new_files

def initiate_session(hostname, address, password):
    session = imaplib.IMAP4_SSL(hostname, 993)
    session.login(address, password)

    session.select('Inbox')
    status, inbox_data = session.search(None,'ALL')
    inbox_data = inbox_data[0].split(" ")

    return dict(
        session = session,
        inbox = inbox_data)

def fetch_subject_mime_parts(session, mid):
    """
    Retrieves the message specified by mid, returning
    a tuple of subject and MIME parts.
    """
    subj_resp = session.fetch(mid, '(RFC822.SIZE BODY[HEADER.FIELDS (SUBJECT)])')
    s_parts = subj_resp[1][0][1].split(":")
    subject = ":".join(s_parts[1:]).strip()
    resp = session.fetch(mid, '(UID BODY[TEXT])')
    resplines = resp[1][0][1].split('\r\n')
    parts = []
    marker = resplines[0] or resplines[1]
    for rl in resplines:
        if rl == marker:
            parts.append([])
        elif parts and rl:
            parts[len(parts)-1].append(rl)
    return (subject, parts)

if __name__ == "__main__":
    fetch_update_emails('imap.gmail.com', secrets.address, secrets.password)
