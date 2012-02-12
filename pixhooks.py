import Image
import json
import time
import secrets
import pdb
import twitter

GALLERY_SIZE_LIMIT = 20

def process_update_email(subject, parts):
    '''
    Process an update email, given a subject and its composite MIME parts.
    subject - (string) Subject line of the email
    parts - (tuple) MIME parts of the email, ex: ((data, type), (data, type),...)
    Raises on failure
    '''
    images = []
    new_files = []
    do_tweet = False
    description = ""
    for part, part_type in parts:
        if 'text/' in part_type:
            for line in part:
                if '#tw' in line:
                    do_tweet = True
                    line.replace('#tw','')
                if line.replace(' ',''):
                    description += line.strip()+"\n"
        if 'image/' in part_type:
            images.append((image_from_mime_part(part), part_type))
            new_files += store_images_metadata(images, description, subject)
    update_gallery(new_files)
    if do_tweet:
        tweet_about(new_files)

def update_gallery(new_files):
    f = open(secrets.static_dir+'/gallery.json','r')
    gallery_str = f.read()
    f.close()
    if gallery_str:
        gallery = json.loads(gallery_str)
    else:
        gallery = []
    gallery = new_files + gallery
    gallery_str = json.dumps(gallery[:GALLERY_SIZE_LIMIT])
    f = open(secrets.static_dir+'/gallery.json','w')
    f.write(gallery_str)
    f.close()

def tweet_about(new_files):
    api = twitter.Api(**secrets.twitter)
    if new_files:
        first_file = new_files[0]
        first_url = secrets.picture_path + first_file['big'].split('/')[-1]
        update = first_file['story'] + " " + first_url
        api.PostUpdate(update)

def image_from_mime_part(part):
    base64buffer = ''
    for line in part:
        if ':' in line or ('=' in line and line[-1] != '='):
            pass
        else:
            base64buffer += line
    return base64buffer.decode('base64')
    
def store_images_metadata(images, description, subject):
    filenames = []

    for idx, image in enumerate(images):
        extension = image[1].split("/")[1].split(" ")[0].split('"')[0]
        filename = "%s_%s.%s" % (
            int(time.time()*10000000),
            idx,
            extension)
        filepath = secrets.static_dir+"/"+filename
        fh = open(filepath, "wb")
        fh.write(image[0])
        fh.close()
        sizes = rotate_and_scale_image(filepath)
        filedict = {'story':subject,
                    'description':description,
                    'orig':filename}
        filedict.update(sizes)
        filenames.append(filedict)
    return filenames


size_small = 200, 200
size_big = 1024, 1024

def rotate_and_scale_image(src_path):
    im = Image.open(src_path)
    exif_data = im._getexif()
    
    # We rotate regarding to the EXIF orientation information
    if exif_data:
        orientation = exif_data.get(274)
        if orientation == 1:
            mirror = im.copy()
        elif orientation == 2:
            mirror = im.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            mirror = im.transpose(Image.ROTATE_180)
        elif orientation == 4:
            mirror = im.transpose(Image.FLIP_TOP_BOTTOM)
        elif orientation == 5:
            mirror = im.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.ROTATE_270)
        elif orientation == 6:
            mirror = im.transpose(Image.ROTATE_270)
        elif orientation == 7:
            mirror = im.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
        elif orientation == 8:
            mirror = im.transpose(Image.ROTATE_90)
        else:
            mirror = im.copy()
    else:
        # No EXIF information, the user has to do it
        mirror = im.copy()

    namer = lambda sep: ".".join(src_path.split(".")[:1])+sep+"."+src_path.split(".")[-1]
    bigname = namer("_big")
    mirror.thumbnail(size_big, Image.ANTIALIAS)
    mirror.save(bigname, "JPEG", quality=85)
    bigname = bigname.split("/")[-1]
    smallname = namer("_small")
    mirror.thumbnail(size_small, Image.ANTIALIAS)
    mirror.save(smallname, "JPEG", quality=85)
    smallname = smallname.split("/")[-1]

    return {'small':smallname,
            'big':bigname}
