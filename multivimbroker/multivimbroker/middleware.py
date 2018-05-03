# Copyright (c) 2017-2018 VMware, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.


import uuid
from onaplogging.mdcContext import MDC
from multivimbroker.pub.config.config import SERVICE_NAME
from multivimbroker.pub.config.config import FORWARDED_FOR_FIELDS


class LogContextMiddleware(object):

    #  the last IP behind multiple proxies,  if no exist proxies
    #  get local host ip.
    def _getLastIp(self, request):

        ip = ""
        try:
            for field in FORWARDED_FOR_FIELDS:
                if field in request.META:
                    if ',' in request.META[field]:
                        parts = request.META[field].split(',')
                        ip = parts[-1].strip().split(":")[0]
                    else:
                        ip = request.META[field].split(":")[0]

            if ip == "":
                ip = request.META.get("HTTP_HOST").split(":")[0]

        except Exception:
            pass

        return ip

    def process_request(self, request):

        # Fetch TRANSACTIONID Id and pass to plugin server
        ReqeustID = request.META.get("HTTP_X_TRANSACTIONID", None)
        if ReqeustID is None:
            ReqeustID = str(uuid.uuid3(uuid.NAMESPACE_URL, SERVICE_NAME))
            request.META["HTTP_X_TRANSACTIONID"] = ReqeustID
        MDC.put("requestID", ReqeustID)
        # generate the unique  id
        InovocationID = str(uuid.uuid3(uuid.NAMESPACE_DNS, SERVICE_NAME))
        MDC.put("invocationID", InovocationID)
        MDC.put("serviceName", SERVICE_NAME)
        # access ip
        MDC.put("serviceIP", self._getLastIp(request))

        return None

    def process_response(self, request, response):

        MDC.clear()
        return response
