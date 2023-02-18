SORT_POSTS_Q = 10

URL_INDEX = ''

URL_GROUP_SLUG = 'group/<slug>/'

URL_PROFILE = 'profile/<str:username>/'

URL_POST_ID = 'posts/<int:post_id>/'

URL_CREATE_POST = 'create/'

URL_POST_EDIT = 'posts/<int:post_id>/edit/'

URL_ADD_COMMENT = 'posts/<int:post_id>/comment'

URL_NAME_INDEX = 'groups:index'

URL_NAME_SLUG = 'groups:group_list'

URL_NAME_ADD_COMMENT = 'groups:add_comment'

URL_NAME_PROFILE = 'groups:profile'

URL_NAME_POST_ID = 'groups:post_detail'

URL_NAME_CREATE = 'groups:post_create'

URL_NAME_POST_EDIT = 'groups:post_update'

URL_NAME_PROFILE_FOLLOW = 'groups:profile_follow'

URL_NAME_PROFILE_UNFOLLOW = 'groups:profile_unfollow'

URL_NAME_FOLLOW = 'groups:follow_index'

TEMPLATE_INDEX = 'posts/index.html'

TEMPLATE_GROUP_POSTS = 'posts/group_list.html'

TEMPLATE_PROFILE = 'posts/profile.html'

TEMPLATE_POST_ID = 'posts/post_detail.html'

TEMPLATE_CREATE = 'posts/create_post.html'

TEMPLATE_EDIT = 'posts/update_post.html'
