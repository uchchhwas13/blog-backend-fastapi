from src.repositories.comment_repository import CommentRepository
from src.models.comment import Comment as CommentModel
from src.models.user import User
from src.schemas.blog import CommentCreateModel, UserInfo, Comment, CommentResponse
from src.utils import build_file_url
from src.exceptions import ResourceNotFoundError, DatabaseError, AuthorizationError


class CommentService:
    def __init__(self, comment_repo: CommentRepository):
        self.comment_repo = comment_repo

    async def add_comment(
        self,
        comment_data: CommentCreateModel,
        user: User
    ) -> CommentResponse:
        try:
            comment = CommentModel(
                **comment_data.model_dump(),
            )
            created_comment = await self.comment_repo.create(comment)
            return self._to_comment_response(created_comment, user)
        except Exception:
            raise DatabaseError("Failed to add comment")

    async def update_comment(
        self,
        comment_id: str,
        new_content: str,
        user: User
    ) -> CommentResponse:
        comment = await self.comment_repo.get_by_id(comment_id)

        if comment is None:
            raise ResourceNotFoundError("Comment", comment_id)

        if comment.author.id != user.id:
            raise AuthorizationError(
                "You are not allowed to edit this comment")

        comment.content = new_content
        updated_comment = await self.comment_repo.update(comment)

        return self._to_comment_response(updated_comment, user)

    def _to_comment_response(self, comment: CommentModel, author: User) -> CommentResponse:
        return CommentResponse(
            comment=Comment(
                id=str(comment.id),
                content=comment.content,
                created_by=UserInfo(
                    id=str(author.id),
                    name=author.name,
                    image_url=build_file_url(author.profile_image_url)
                ),
                created_at=comment.created_at
            )
        )
