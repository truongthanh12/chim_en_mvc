def modify_input_for_multiple_files(property_id, image):
    dict = {}
    dict['product'] = property_id
    dict['image'] = image
    return dict


def modify_input_for_single_image(image):
    dict = {}
    dict['image'] = image
    return dict
