// World initialisation data

game.value ('World', {
    initial: {
        size: {width: 2048, height: 2048},
        panStart: {x:0, y:0},
        zoomStart: 3,
        zoomMax: 3,
        viewportRestricted: true,
        locations: [
            {
                name: 'Shipwreck',
                region: [580,150,150,110],
                bgImage: 'beached-shipwreck.png',
                items: [
                    {
                        name: 'Ruined Ship',
                        region: [400,330,270,140],
                    },
                    {
                        name: 'Note',
                        region: [260,355,40,50],
                        closeUpImage: 'beach-note.png',
                        features: [
                            {
                                name: 'test feature',
                                region: [100,100,100,100],
                            }
                        ],
                    },
                ]
            },
            {
                name: 'Old Shed',
                region: [910,500,90,75],
                bgImage: 'forest-clearing.jpg',
                items: [
                    {
                        name: 'Door',
                        region: [170,230,90,210],
                    },
                    {
                        name: 'Large Wheels',
                        region: [290,260,160,140],
                    },
                ]
            },
            {
                name: 'House',
                region: [540,540,160,140],
                bgImage: 'jeb-house-interior.jpg',
                items: [
                ]
            },
        ],
    },
});

