import pyftpdlib.authorizers
import pyftpdlib.handlers
import pyftpdlib.servers


def main():
    # '가상' 사용자를 관리하기 위한 더미 권한 관리자를 인스턴스화합니다.
    authorizer = pyftpdlib.authorizers.DummyAuthorizer()

    # 전체 권한을 가진 새 사용자와 읽기 전용 익명 사용자를 정의합니다.
    authorizer.add_user("user", "12345", ".", perm="elradfmwM")
    authorizer.add_anonymous(".", perm="elradfmwM")

    # FTP 핸들러 클래스를 인스턴스화합니다.
    handler = pyftpdlib.handlers.FTPHandler
    handler.authorizer = authorizer

    # 클라이언트가 연결할 때 반환되는 문자열인 사용자 지정 배너를 정의합니다.
    handler.banner = "pyftpdlib 기반 ftpd 준비 완료."

    # NAT 뒤에 있는 경우 마스커레이드 주소와 패시브 연결에 사용할 포트 범위를 지정합니다.
    # handler.masquerade_address = '151.25.42.11'
    # handler.passive_ports = range(60000, 65535)

    # FTP 서버 클래스를 인스턴스화하고 0.0.0.0:2121에서 수신 대기합니다.
    address = ("", 2121)
    server = pyftpdlib.servers.FTPServer(address, handler)

    # 연결 제한을 설정합니다.
    server.max_cons = 256
    server.max_cons_per_ip = 5

    # FTP 서버 시작
    server.serve_forever()


if __name__ == "__main__":
    main()
