from tdmclient import ClientAsync
from led_change import change_color

with ClientAsync() as client:
    async def prog():
        print("Starting LED sequence...")
        with await client.lock() as node:
            # Blue
            print("Setting Blue")
            # error = await node.compile(led_blue)
            error = await change_color(node, "blue")
            if error is not None:
                print(f"Compilation error: {error['error_msg']}")
                return
            await node.run()
            await client.sleep(2)

            # Green
            print("Setting Green")
            # error = await node.compile(led_green)
            error = await change_color(node, "green")
            if error is not None:
                print(f"Compilation error: {error['error_msg']}")
                return
            await node.run()
            await client.sleep(2)

            # Red
            print("Setting Red")
            # error = await node.compile(led_red)
            error = await change_color(node, "red")
            if error is not None:
                print(f"Compilation error: {error['error_msg']}")
                return
            await node.run()
            await client.sleep(2)

            # Back to Blue
            print("Back to Blue")
            # error = await node.compile(led_blue)
            error = await change_color(node, "blue")
            if error is not None:
                print(f"Compilation error: {error['error_msg']}")
                return
            await node.run()
            await client.sleep(2)

    print("Program started")
    client.run_async_program(prog)
    print("Program finished")