from bs4 import BeautifulSoup

from WeiboForwardBot.fetch.weibo_post import WeiboPost


class Format:
    @staticmethod
    def create_href_tag(link: str, text: str) -> str:
        return f'<a href="{link}">{text}</a>'

    @staticmethod
    def compose_html_message(weibo_post: WeiboPost) -> str:
        weibo_post._html_text = weibo_post._html_text.replace('href="/status/', 'href="https://m.weibo.cn/status/')
        original_message = (
            f"<b>{weibo_post._author_name}</b> @ {weibo_post._original_created_time} GMT:\n{weibo_post._html_text} "
            + (
                f'<b> {Format.create_href_tag(weibo_post._original_post_link, "打开微博")}</b>'
                if not weibo_post._is_long_text
                else ""
            )
            + "\n"
            + "\n".join(
                [Format.create_href_tag(pic_link, f"图片附件_{idx}") for idx, pic_link in enumerate(weibo_post._pic_link)]
            )
            + "\n"
        )

        if weibo_post.is_retweet:
            retweet_message = (
                f"<b>{weibo_post._retweet_author_name}</b> @ {weibo_post._retweet_time} GMT:\n{weibo_post._retweet_comment} "
                + f'<b>{Format.create_href_tag(weibo_post._retweet_post_link, "打开微博")}</b> \n（转发）\n'
            )
        else:
            retweet_message = ""
        combined_message = retweet_message + original_message
        return combined_message

    @staticmethod
    def reformat_html_message(message: str) -> str:
        message = message.replace("<br />", "\n")
        soup = BeautifulSoup(message, "html.parser")
        for tag in soup.find_all("span", {"class": "url-icon"}):
            tag.replaceWith("")
        for tag in soup.find_all("span", {"class": "surl-text"}):
            tag.unwrap()
        return str(soup)

    @staticmethod
    def preview_on(message: str) -> bool:
        """
        if message has link to .jpg
        :param message:
        :return:
        """
        return message.find(".jpg") >= 0
