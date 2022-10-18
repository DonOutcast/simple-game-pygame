import pygame

def crop_img(filename, size):
    ''' обрезает картинку, оставляя только одну из непрозрачных частей, и устанавливает масштаб size % '''
    img = pygame.image.load(filename).convert_alpha() # 
    rects = pygame.mask.from_surface(img).get_bounding_rects() # взяв маску изображения, получаем список непустых прямоугольников
    if rects:
        rect = rects[0] # мы не предполагаем, что в файле несколько отдельных картинок, поэтому берём всегда первую из списка
        cropped = pygame.Surface([rect.width, rect.height], pygame.SRCALPHA) # пустая картинка нужных размеров, ПРОЗРАЧНАЯ
        cropped.blit(img, (0, 0), rect) # рисуем на созданной пустой заговке кусок (rect) из переданной картинки
    else:
        cropped = pygame.Surface(1, 1)
        rect = cropped.get_rect()
    # дальше меняем масштаб (size - это число процентов):
    width = round(rect.width * size / 100)
    height = round(rect.height * size / 100)
    return pygame.transform.scale(cropped, (width, height))      

def repeat_img(image, times):
    ''' повторяет одну и ту же картинку по горизонтали, возвращает картинку, составленную из них всех'''
    if times > 0:
        rect = image.get_rect()
        w = rect.width
        img = pygame.Surface((w * times, rect.height), pygame.SRCALPHA)
        for i in range(times):
            img.blit(image, (w * i, 0))
    else:
        img = pygame.Surface(1, 1)
    return img

def append_img(image1, image2):
    ''' соединяет две картинки по горизонтали (используя высоту первой)'''
    rect1 = image1.get_rect()
    rect2 = image2.get_rect()
    w = rect1.width + rect2.width
    img = pygame.Surface([w, rect1.height], pygame.SRCALPHA)
    img.blit(image1, (0, 0))
    img.blit(image2, (rect1.width, 0))
    return img

def append_img3(image1, image2, image3, n):
    ''' соединяет три картинки по горизонтали, повторяя среднюю n раз'''
    img_l = image1
    if n > 0:
        img_l = append_img(img_l, repeat_img(image2, n))    
    img = append_img(img_l, image3)
    return img

