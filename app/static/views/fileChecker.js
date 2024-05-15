// Function to check if a single file is a valid JPEG or PNG
function validateSingleFile(file, callback) {
    if (file) {
        if (file.type === 'image/jpeg' || file.type === 'image/png') {
            callback(true);
        } else {
            callback(false);
        }
    } else {
        callback(false);
    }
}

// Function to check if two files are valid JPEG or PNG
function validateTwoFiles(file1, file2, callback) {
    validateSingleFile(file1, function(validFile1) {
        if (validFile1) {
            validateSingleFile(file2, function(validFile2) {
                callback(validFile2);
            });
        } else {
            callback(false);
        }
    });
}
