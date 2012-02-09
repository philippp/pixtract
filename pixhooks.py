import json
import time
import secrets
import pixsize

def process_update_email(subject, parts):
    '''
    Process an update email, given a subject and its composite MIME parts.
    subject - (string) Subject line of the email
    parts - (tuple) MIME parts of the email, ex: ((data, type), (data, type),...)
    Raises on failure
    '''
    images = []
    new_files = []
    for part, part_type in parts:
        if 'image/' in part_type:
            images.append((image_from_mime_part(part), part_type))
            new_files += store_images_metadata(images,subject)
    update_gallery(new_files)

def update_gallery(new_files):
    f = open(secrets.static_dir+'/gallery.json','r')
    gallery_str = f.read()
    f.close()
    if gallery_str:
        gallery = json.loads(gallery_str)
    else:
        gallery = []
    gallery = new_files + gallery
    gallery_str = json.dumps(gallery)
    f = open(secrets.static_dir+'/gallery.json','w')
    f.write(gallery_str)
    f.close()

def image_from_mime_part(part):
    base64buffer = ''
    for line in part:
        if ':' in line or ('=' in line and line[-1] != '='):
            pass
        else:
            base64buffer += line
    return base64buffer.decode('base64')
    
def store_images_metadata(images, subject):
    filenames = []

    for idx, image in enumerate(images):
        filename = "%s_%s.%s" % (
            int(time.time()*10000000),
            idx,
            image[1].split("/")[1])
        filepath = secrets.static_dir+"/"+filename
        fh = open(filepath, "wb")
        fh.write(image[0])
        fh.close()
        sizes = pixsize.size_image(filepath)
        filedict = {'story':subject,
                    'orig':filename}
        filedict.update(sizes)
        filenames.append(filedict)
    return filenames
