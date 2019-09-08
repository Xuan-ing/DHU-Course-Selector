import numpy as np
from PIL import Image



# 转化图片格式到矩阵 返回矩阵
def image2matrix(path, image_size):
    matrices = []
    for i in range(image_size):
        if i < 10:
            img = Image.open(path + '00' + str(i) + '.bmp')
        elif i < 100:
            img = Image.open(path + '0' + str(i) + '.bmp')
        else:
            img = Image.open(path + str(i) + '.bmp')

        img = img.convert('L')
        matrix = np.array(img, dtype=np.int32)
        for column in range(matrix.shape[1]):
            for row in range(matrix.shape[0]):
                matrix[row, column] = 1 if matrix[row, column] == 255 else 0
       
        matrices.append(matrix)
    return matrices

'''

# 获得边界矩阵 返回边界 (第1问)
def get_boundary_matrix(matrices):
    vertical_length = matrices[0].shape[0]
    horizontal_length = matrices[0].shape[1]

    boundaries = []
    for i in range(image_size):
        boundaries.append([matrices[i][:, 0], matrices[i][:, -1]])

    return boundaries

# 计算平方和
def calc_square_sum(boundaries):
    squares = []
    for i in range(image_size):
        for j in range(image_size):
            squares.append(np.square(boundaries[i][1] - boundaries[j][0]))
    return squares

'''

def feature_grey_vector(matrices, language):
    vectors = []
    for matrix in matrices:
        vector = np.zeros(matrix.shape[0])
        for i in range(matrix.shape[0]):
            if language == 'Chinese':
                if 0 not in list(matrix[i]):
                    vector[i] = 1
            elif language == 'English':
                if np.sum(matrix[i]) >= 56:
                    vector[i] = 1
        vectors.append(vector)
    
    return vectors


# 尝试对文本进行行分组 (中英相同)
def text_group_by_row(vectors):
    # formal_line = 100
    visited = np.zeros(len(vectors), dtype=np.uint8)
    groups = []
    for i in range(len(vectors)):
        if visited[i] != 0:
            continue
        group = [i]
        visited[i] = 1
        for j in range(len(vectors)):
            if i == j or visited[j] != 0:
                continue
            # (中文)if np.sum(np.square(vectors[i][0:120] - vectors[j][0:120])) < 15:
            if np.sum(np.square(vectors[i] - vectors[j])) < 20:

                group.append(j)
                visited[j] = 1
        groups.append(group)

    return groups

def main():
    image_size = 209
    matrices = image2matrix('B\\附件4\\', image_size)
    vectors = feature_grey_vector(matrices, 'English')
    print([len(vector) for vector in text_group_by_row(vectors)], end=' ')

    # boundaries = get_boundary_matrix(matrices)
    # squares = calc_square_sum(boundaries)

if __name__ == '__main__':
    main()