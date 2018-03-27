def push_to_imgur(filename):
    import pyimgur
    filename = filename.replace(' ','_')
    filename = filename.replace('(','')
    filename = filename.replace(')','')
    import PIL
    from PIL import Image, ImageEnhance
    im = Image.open(filename)
    basewidth = 1000
    wpercent = (basewidth / float(im.size[0]))
    hsize = int((float(im.size[1]) * float(wpercent)))
    im = im.resize((basewidth, hsize), PIL.Image.ANTIALIAS)  

    im = im.convert('L')

    contrast = ImageEnhance.Contrast(im)

    im = contrast.enhance(5)
    im.save(filename)
    CLIENT_ID = "0e5d2ae51739238"
    PATH = filename
    im = pyimgur.Imgur(CLIENT_ID)
    uploaded_image = im.upload_image(PATH, title="Uploaded for HWR")
    #print(uploaded_image.title)
    return uploaded_image.link
    #print(uploaded_image.size)
    #print(uploaded_image.type)