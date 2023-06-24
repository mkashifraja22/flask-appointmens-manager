doc_table = """

<div class="table-responsive p-0">
    <table class="table align-items-center justify-content-center mb-0">
        <thead>
        <tr>
            <th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">
                File Name
            </th>
            <th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7 ps-2">
                Download
            </th>
           

        </tr>
        </thead>
        <tbody>
        {% for doc in docs %}
            <tr>
                <td>
                    <div class="d-flex px-2">

                        <div class="my-auto">
                            <h6 class="mb-0 text-sm">{{ doc.file_name }}</h6>
                        </div>
                    </div>
                </td>
                <td>
                    <p class="text-sm font-weight-bold mb-0"><a
                            href="{{ url_for('download_file',filename=doc.file_name) }}" download>Download File</a>
                    </p>
                </td>
               

            </tr>
        {% endfor %}
        </tbody>
    </table>
</div>
"""