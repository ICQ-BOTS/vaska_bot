box.cfg{
    listen=3301
}

box.schema.user.grant('guest', 'read,write,execute', 'universe', nil, {if_not_exists=true})

box.once("vaska_bot", function()
    box.schema.sequence.create('phrases_S')
    box.schema.space.create('phrases', {
        if_not_exists = true,
        format={
            {name = 'id', type = 'unsigned'}
        }
    })
    box.space.phrases:create_index('id', {
        sequence = 'phrases_S',
        parts = {'id'}
    }) 
    box.schema.sequence.create('question_S')
    box.schema.space.create('question', {
        if_not_exists = true,
        format={
            {name = 'id', type = 'unsigned'}
        }
    })
    box.space.question:create_index('id', {
        sequence = 'question_S',
        parts = {'id'}
    })
    box.schema.space.create('user', {
        if_not_exists = true,
        format={
            {name = 'user_id', type = 'string'},
            {name = 'example', type = 'boolean'},
            {name = 'old_mes', type = 'map'}
        }
    })
    box.space.user:create_index('id', {
        type = 'hash',
        parts = {'user_id'},
        if_not_exists = true,
        unique = true
    })
    box.schema.sequence.create('sticker_S')
    box.schema.space.create('sticker', {
        if_not_exists = true,
        format={
            {name = 'id', type = 'unsigned'},
            {name = 'sticker', type = 'string'}
        }
    })
    box.space.sticker:create_index('id', {
        sequence = 'sticker_S',
        parts = {'id'}
    })        
end
)


