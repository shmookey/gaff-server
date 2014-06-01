game.service ('Assets', function () {
    this.imageRefs = {};

    this.getImageURI = function (imageName) {
        return this.imageRefs[imageName];
    };

    return this;
});
