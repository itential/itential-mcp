# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from itential_mcp.models import automation_studio as models


class TestTextFSMTemplate:
    """Tests for TextFSMTemplate model."""

    def test_textfsm_template_creation(self):
        """Test creating a TextFSM template with valid data."""
        template_data = {
            "_id": "68c31fc5f7a1e4d40186b6d5",
            "name": "ACL Parser",
            "group": "Network Parsers",
            "description": "Parse Cisco ACL configurations",
            "template": "Value Required,Filldown ACL_NAME (\\S+)\nValue ACL_TYPE (standard|extended)\nValue ACTION (permit|deny)\nValue PROTOCOL ([a-z]+)\n\nStart\n  ^ip\\s+access-list\\s+${ACL_TYPE}\\s+${ACL_NAME}\\s* -> Record\n  ^\\s+${ACTION}\\s+${PROTOCOL}\\s+.* -> Record\n\nEOF",
            "data": "ip access-list extended sample\n permit tcp host 10.1.1.1 any\n deny ip any any",
            "command": "show access-list",
            "type": "textfsm",
            "created": "2025-09-11T19:15:17.397Z",
            "lastUpdated": "2025-09-11T19:15:17.397Z",
            "createdBy": "67eaf8b49b093bfbf0e62a9f",
            "lastUpdatedBy": "67eaf8b49b093bfbf0e62a9f",
            "tags": []
        }

        template = models.TextFSMTemplate(**template_data)

        assert template.id == "68c31fc5f7a1e4d40186b6d5"
        assert template.name == "ACL Parser"
        assert template.group == "Network Parsers"
        assert template.description == "Parse Cisco ACL configurations"
        assert template.type == "textfsm"
        assert template.command == "show access-list"
        assert "Value Required,Filldown ACL_NAME" in template.template
        assert "ip access-list extended sample" in template.data
        assert len(template.tags) == 0

    def test_textfsm_template_with_complex_parsing(self):
        """Test TextFSM template with complex parsing rules."""
        template_data = {
            "_id": "template123",
            "name": "Complex ACL Parser",
            "group": "Advanced Parsers",
            "description": "Parse complex ACL with multiple value types",
            "template": """Value Required,Filldown ACL_NAME (\\S+)
Value Filldown ACL_TYPE (standard|extended)
Value COMMENT (.*)
Value ACTION (permit|deny)
Value PROTOCOL ([a-z]+)
Value SRC_HOST (\\d+\\.\\d+\\.\\d+\\.\\d+)
Value SRC_ANY (any)
Value SRC_NETWORK (\\d+\\.\\d+\\.\\d+\\.\\d+)
Value SRC_WILDCARD (\\d+\\.\\d+\\.\\d+\\.\\d+)
Value SRC_PORT_MATCH (eq|range|lt|gt)
Value SRC_PORT ((?<!range\\s)\\S+)
Value SRC_PORT_RANGE_START ((?<!range\\s)\\S+)
Value SRC_PORT_RANGE_END (\\S+)
Value DST_HOST (\\d+\\.\\d+\\.\\d+\\.\\d+)
Value DST_ANY (any)
Value DST_NETWORK (\\d+\\.\\d+\\.\\d+\\.\\d+)
Value DST_WILDCARD (\\d+\\.\\d+\\.\\d+\\.\\d+)
Value DST_PORT_MATCH (eq|range|lt|gt)
Value DST_PORT ((?<!range\\s)\\S+)
Value DST_PORT_RANGE_START ((?<=range\\s)\\S+)
Value DST_PORT_RANGE_END (\\S+)
Value LOG (log-input|log)
Value TIME (\\S+)

Start
  # Clear all data to start new named ACL
  ^(ip\\s+|)access-list -> Continue.Clearall
  # Record new named ACL
  ^ip\\s+access-list\\s+${ACL_TYPE}\\s+${ACL_NAME}\\s* -> Record
  # Record named ACL Extended entry
  ^\\s+${ACTION}\\s+${PROTOCOL}\\s+(host\\s+${SRC_HOST}|${SRC_ANY}|${SRC_NETWORK}\\s+${SRC_WILDCARD})(\\s+${SRC_PORT_MATCH}\\s+(${SRC_PORT_RANGE_START}\\s+${SRC_PORT_RANGE_END}|${SRC_PORT})|)\\s+(host\\s+${DST_HOST}|${DST_ANY}|${DST_NETWORK}\\s+${DST_WILDCARD})(\\s+${DST_PORT_MATCH}\\s+(${DST_PORT_RANGE_START}\\s+${DST_PORT_RANGE_END}|${DST_PORT})|)(\\s+${LOG}|)(\\s+time-range\\s+${TIME}|) -> Record
  # Record named ACL Standard entry
  ^\\s+${ACTION}\\s+(${SRC_NETWORK}\\s+${SRC_WILDCARD}|${SRC_ANY}|${SRC_HOST})(\\s+${LOG}|)(\\s+time-range\\s+${TIME}|)\\s* -> Record
  # Record named ACL Remark
  ^\\s+remark\\s+${COMMENT}\\s*
  # Record numbered ACL Extended entry
  ^access-list\\s+${ACL_NAME}\\s+${ACTION}\\s+${PROTOCOL}\\s+(host\\s+${SRC_HOST}|${SRC_ANY}|${SRC_NETWORK}\\s+${SRC_WILDCARD})(\\s+${SRC_PORT_MATCH}\\s+(${SRC_PORT_RANGE_START}\\s+${SRC_PORT_RANGE_END}|${SRC_PORT})|)\\s+(host\\s+${DST_HOST}|${DST_ANY}|${DST_NETWORK}\\s+${DST_WILDCARD})(\\s+${DST_PORT_MATCH}\\s+(${DST_PORT_RANGE_START}\\s+${DST_PORT_RANGE_END}|${DST_PORT})|)(\\s+${LOG}|)(\\s+time-range\\s+${TIME}|)\\s* -> Record
  # Record numbered ACL Standard entry
  ^access-list\\s+${ACL_NAME}\\s+${ACTION}\\s+(${SRC_NETWORK}\\s+${SRC_WILDCARD}|${SRC_ANY}|${SRC_HOST})(\\s+${LOG}|)(\\s+time-range\\s+${TIME}|)\\s* -> Record
  # Record numbered ACL Remark
  ^access-list\\s+${ACL_NAME}\\s+remark\\s+${COMMENT}\\s* -> Record
  # Catch all unuseful raw data
  ^(!\\s*|$$|Building configuration.*|Current configuration.*|Configuration.*|end.*)
  # Error out if raw data does not match any above rules.
  ^.* -> Error "Could not parse line:"

EOF""",
            "data": "Building configuration...\n\nCurrent configuration : 5066 bytes\n!\nConfiguration of Partition - access-list\n!\n!\n!\n!\nip access-list extended sample\n remark \"allows BGP\"\n permit tcp host 10.1.6.20 host 10.1.6.98 eq bgp\n permit tcp host 10.1.6.20 eq bgp host 10.1.6.98\n remark \"allows sample to ping\"\n permit icmp 10.1.6.16 0.0.0.3 host 10.1.6.98\n permit icmp 10.1.6.24 0.0.0.7 host 10.1.6.98\n remark \"allows sample to ping\"\n permit icmp 10.1.6.16 0.0.0.3 host 10.1.5.20\n permit icmp 10.1.6.24 0.0.0.7 host 10.1.5.20\n remark \"allows sample to ping\"\n permit icmp 10.1.6.16 0.0.0.3 host 10.1.6.144\n permit icmp 10.1.6.24 0.0.0.7 host 10.1.6.144\n remark \"allows sample to ping\"\n permit icmp 10.1.6.16 0.0.0.3 host 10.1.6.146\n permit icmp 10.1.6.24 0.0.0.7 host 10.1.6.146\n remark \"allows sample to ping\"\n permit icmp 10.1.6.16 0.0.0.3 host 10.1.6.148\n permit icmp 10.1.6.24 0.0.0.7 host 10.1.6.148\n remark \"allows sample to ping\"\n permit icmp 10.1.6.16 0.0.0.3 host 10.1.6.152\n permit icmp 10.1.6.24 0.0.0.7 host 10.1.6.152\n remark allows sample to ping\n permit icmp 10.1.6.16 0.0.0.3 host 10.1.8.26\n permit icmp 10.1.6.24 0.0.0.7 host 10.1.8.26\n remark allows sample to ping\n permit icmp 10.1.6.16 0.0.0.3 host 10.1.8.152\n permit icmp 10.1.6.24 0.0.0.7 host 10.1.8.152\n remark permit sample servers to ping\n permit icmp 10.1.6.16 0.0.0.3 10.3.14.0 0.0.0.127\n permit icmp 10.1.6.24 0.0.0.7 10.3.14.0 0.0.0.127\n remark allows sample to ping\n permit icmp 10.1.6.16 0.0.0.3 host 10.3.139.248\n permit icmp 10.1.6.24 0.0.0.7 host 10.3.139.248\n permit icmp 10.1.6.16 0.0.0.3 10.3.139.128 0.0.0.7\n permit icmp 10.1.6.24 0.0.0.7 10.3.139.128 0.0.0.7\n remark \"allows sample workstation(s) to connect\"\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.5.20 eq 4000\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.5.20 eq 4010\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.5.20 eq 4020\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.5.20 eq 4080\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.5.20 eq 4300\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.5.20 eq 4310\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.5.20 eq 4320\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.5.20 eq 4380\n remark \"allows sample workstation(s)\"\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.144 eq 4000\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.144 eq 4010\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.144 eq 4020\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.144 eq 4300\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.144 eq 4310\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.144 eq 4320\n remark \"allows sample workstation(s)\"\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.146 eq 4000\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.146 eq 4010\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.146 eq 4020\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.146 eq 4300\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.146 eq 4310\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.146 eq 4320\n remark \"allows sample workstation(s)\"\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.148 eq 4050\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.148 eq 4060\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.148 eq 4350\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.148 eq 4360\n remark \"allows sample workstation(s)\"\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.152 eq 4000\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.152 eq 4010\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.152 eq 4020\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.152 eq 4080\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.152 eq 4300\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.152 eq 4310\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.152 eq 4320\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.6.152 eq 4380\n remark permit sample workstation(s)\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.8.26 eq 4001\n remark permit sample workstation(s)\n permit tcp 10.1.6.24 0.0.0.7 host 10.1.8.152 eq 4001\n remark permit sample to connect\n permit tcp 10.1.6.24 0.0.0.7 10.3.14.64 0.0.0.31 eq 9815\n permit tcp 10.1.6.24 0.0.0.7 10.3.14.64 0.0.0.31 range 9821 9823\n remark permit sample to connect\n permit tcp 10.1.6.24 0.0.0.7 10.3.14.96 0.0.0.31 range 7400 7407\n remark permit sample UDP access\n permit udp 10.1.6.16 0.0.0.3 host 10.3.139.133 range 13001 13191\n permit udp 10.1.6.24 0.0.0.7 host 10.3.139.133 range 13001 13191\n remark permit sample TCP access\n permit tcp 10.1.6.16 0.0.0.3 host 10.3.139.134 range 13001 13191 log time-range test\n permit tcp 10.1.6.24 0.0.0.7 host 10.3.139.134 range 13001 13191 log-input\n remark allow sample to send PIM-Join\n permit pim host 10.1.6.20 host 224.0.0.1\n deny   ip any any\n permit ip 10.0.0.0 0.255.0.255 any\nip access-list extended test\naccess-list 97 remark this is a remark\naccess-list 97 deny   10.1.0.1 0.0.255.0 log\naccess-list 97 permit any\naccess-list 98 permit 10.16.5.19\naccess-list 98 permit 10.16.5.20\naccess-list 99 permit 10.16.5.19\naccess-list 99 permit 10.16.5.20\naccess-list 199 permit tcp 10.16.5.19 0.0.0.0 any eq 80\naccess-list 199 permit udp any any eq 1000\naccess-list 101 permit tcp any host 10.1.1.1 eq www\naccess-list 101 permit tcp any host 10.1.1.1 eq 443 log\naccess-list 101 remark this is a remark\naccess-list 101 permit ahp any any log-input\naccess-list 101 permit tcp host 10.1.1.1 eq ftp any eq tacacs log time-range test\n\n!\nip access-list standard stdacl\n permit 10.1.1.1\nip access-list extended test2\n\naccess-list 198 permit tcp 10.16.5.19 0.0.0.0 any eq 80\naccess-list 198 permit udp any any eq 1000\n\nend",
            "command": "show access-list",
            "type": "textfsm",
            "created": "2025-09-11T19:15:17.397Z",
            "lastUpdated": "2025-09-11T19:18:00.060Z",
            "createdBy": "67eaf8b49b093bfbf0e62a9f",
            "lastUpdatedBy": "67eaf8b49b093bfbf0e62a9f",
            "tags": []
        }

        template = models.TextFSMTemplate(**template_data)

        assert template.id == "template123"
        assert template.name == "Complex ACL Parser"
        assert template.group == "Advanced Parsers"
        assert template.type == "textfsm"
        assert "Value Required,Filldown ACL_NAME" in template.template
        assert "Start" in template.template
        assert "EOF" in template.template
        assert "Building configuration" in template.data
        assert len(template.tags) == 0


class TestCreateTextFSMTemplateRequest:
    """Tests for CreateTextFSMTemplateRequest model."""

    def test_create_textfsm_template_request_creation(self):
        """Test creating a CreateTextFSMTemplateRequest with valid data."""
        request = models.CreateTextFSMTemplateRequest(
            name="ACL Parser",
            group="Network Parsers",
            description="Parse Cisco ACL configurations",
            template="Value Required,Filldown ACL_NAME (\\S+)\nValue ACL_TYPE (standard|extended)\nValue ACTION (permit|deny)\nValue PROTOCOL ([a-z]+)\n\nStart\n  ^ip\\s+access-list\\s+${ACL_TYPE}\\s+${ACL_NAME}\\s* -> Record\n  ^\\s+${ACTION}\\s+${PROTOCOL}\\s+.* -> Record\n\nEOF",
            data="ip access-list extended sample\n permit tcp host 10.1.1.1 any\n deny ip any any",
            command="show access-list"
        )

        assert request.name == "ACL Parser"
        assert request.group == "Network Parsers"
        assert request.description == "Parse Cisco ACL configurations"
        assert "Value Required,Filldown ACL_NAME" in request.template
        assert "ip access-list extended sample" in request.data
        assert request.command == "show access-list"

    def test_create_textfsm_template_request_defaults(self):
        """Test CreateTextFSMTemplateRequest with default values."""
        request = models.CreateTextFSMTemplateRequest(
            name="Simple Parser",
            group="Basic Parsers",
            description="Simple parsing template",
            template="Value NAME (\\S+)\n\nStart\n  ^${NAME} -> Record\n\nEOF"
        )

        assert request.name == "Simple Parser"
        assert request.group == "Basic Parsers"
        assert request.description == "Simple parsing template"
        assert request.data == ""
        assert request.command == ""


class TestCreateTextFSMTemplateResponse:
    """Tests for CreateTextFSMTemplateResponse model."""

    def test_create_textfsm_template_response_creation(self):
        """Test creating a CreateTextFSMTemplateResponse with valid data."""
        response_data = {
            "created": {
                "_id": "68c31fc5f7a1e4d40186b6d5",
                "name": "ACL Parser",
                "group": "Network Parsers",
                "description": "Parse Cisco ACL configurations",
                "template": "Value Required,Filldown ACL_NAME (\\S+)\nValue ACL_TYPE (standard|extended)\nValue ACTION (permit|deny)\nValue PROTOCOL ([a-z]+)\n\nStart\n  ^ip\\s+access-list\\s+${ACL_TYPE}\\s+${ACL_NAME}\\s* -> Record\n  ^\\s+${ACTION}\\s+${PROTOCOL}\\s+.* -> Record\n\nEOF",
                "data": "ip access-list extended sample\n permit tcp host 10.1.1.1 any\n deny ip any any",
                "command": "show access-list",
                "type": "textfsm",
                "created": "2025-09-11T19:15:17.397Z",
                "lastUpdated": "2025-09-11T19:15:17.397Z",
                "createdBy": "67eaf8b49b093bfbf0e62a9f",
                "lastUpdatedBy": "67eaf8b49b093bfbf0e62a9f",
                "tags": []
            },
            "edit": "/automation-studio/#/edit?tab=0&template=68c31fc5f7a1e4d40186b6d5"
        }
        
        response = models.CreateTextFSMTemplateResponse(**response_data)

        assert response.created.id == "68c31fc5f7a1e4d40186b6d5"
        assert response.created.name == "ACL Parser"
        assert response.created.type == "textfsm"
        assert response.edit == "/automation-studio/#/edit?tab=0&template=68c31fc5f7a1e4d40186b6d5"


class TestUpdateTextFSMTemplateRequest:
    """Tests for UpdateTextFSMTemplateRequest model."""

    def test_update_textfsm_template_request_creation(self):
        """Test creating an UpdateTextFSMTemplateRequest with valid data."""
        request = models.UpdateTextFSMTemplateRequest(
            name="Updated ACL Parser",
            group="Updated Network Parsers",
            description="Updated parse Cisco ACL configurations",
            template="Value Required,Filldown ACL_NAME (\\S+)\nValue ACL_TYPE (standard|extended)\nValue ACTION (permit|deny)\nValue PROTOCOL ([a-z]+)\n\nStart\n  ^ip\\s+access-list\\s+${ACL_TYPE}\\s+${ACL_NAME}\\s* -> Record\n  ^\\s+${ACTION}\\s+${PROTOCOL}\\s+.* -> Record\n\nEOF",
            data="ip access-list extended updated\n permit tcp host 10.1.1.1 any\n deny ip any any",
            command="show access-list"
        )

        assert request.name == "Updated ACL Parser"
        assert request.group == "Updated Network Parsers"
        assert request.description == "Updated parse Cisco ACL configurations"
        assert "Value Required,Filldown ACL_NAME" in request.template
        assert "ip access-list extended updated" in request.data
        assert request.command == "show access-list"


class TestUpdateTextFSMTemplateResponse:
    """Tests for UpdateTextFSMTemplateResponse model."""

    def test_update_textfsm_template_response_creation(self):
        """Test creating an UpdateTextFSMTemplateResponse with valid data."""
        response_data = {
            "updated": {
                "_id": "68c31fc5f7a1e4d40186b6d5",
                "name": "Updated ACL Parser",
                "group": "Updated Network Parsers",
                "description": "Updated parse Cisco ACL configurations",
                "template": "Value Required,Filldown ACL_NAME (\\S+)\nValue ACL_TYPE (standard|extended)\nValue ACTION (permit|deny)\nValue PROTOCOL ([a-z]+)\n\nStart\n  ^ip\\s+access-list\\s+${ACL_TYPE}\\s+${ACL_NAME}\\s* -> Record\n  ^\\s+${ACTION}\\s+${PROTOCOL}\\s+.* -> Record\n\nEOF",
                "data": "ip access-list extended updated\n permit tcp host 10.1.1.1 any\n deny ip any any",
                "command": "show access-list",
                "type": "textfsm",
                "created": "2025-09-11T19:15:17.397Z",
                "lastUpdated": "2025-09-11T19:18:00.060Z",
                "createdBy": "67eaf8b49b093bfbf0e62a9f",
                "lastUpdatedBy": "67eaf8b49b093bfbf0e62a9f",
                "tags": []
            },
            "edit": "/automation-studio/#/edit?tab=0&template=68c31fc5f7a1e4d40186b6d5"
        }
        
        response = models.UpdateTextFSMTemplateResponse(**response_data)

        assert response.updated.id == "68c31fc5f7a1e4d40186b6d5"
        assert response.updated.name == "Updated ACL Parser"
        assert response.updated.type == "textfsm"
        assert response.edit == "/automation-studio/#/edit?tab=0&template=68c31fc5f7a1e4d40186b6d5"
